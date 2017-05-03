"""
Copyright 2016 ElasticBox All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging

import pymongo
from tornado.gen import coroutine, Return

from api.v1.actions import notifications
from data.query import Query, ObjectNotFoundError


class NamespacesActions(object):

    def __init__(self, settings, user):
        logging.info("Initializing NamespacesActions")

        self.kube = settings["kube"]
        self.database = settings["database"]
        self.oplog = settings["motor"]["local"]["oplog.rs"]

        self.user = user
        self.notifications = ["create", "update"]

    @coroutine
    def check_permissions(self, operation, _request_body):
        logging.debug("check_permissions for user %s and operation %s on namespaces", self.user["username"], operation)
        raise Return(self.user["role"] == "administrator")

    @coroutine
    def create(self, document):
        logging.info("Creating namespace for request %s", document)

        labels = dict()

        if "metadata" in document and "labels" in document["metadata"]:
            labels = document["metadata"]["labels"]

        body = dict(
            kind="Namespace",
            apiVersion="v1",
            metadata=dict(
                name=document["name"],
                labels=labels,
            )
        )

        cursor = self.oplog.find().sort("ts", pymongo.DESCENDING).limit(-1)
        if (yield cursor.fetch_next):
            oplog_entry = cursor.next_object()

            last_timestamp = oplog_entry["ts"]
            logging.info("Watching from timestamp: %s", last_timestamp.as_datetime())
        else:
            last_timestamp = None

        _, namespace = yield [self.kube.namespaces.post(body),
                              self._wait_namespace_creation(cursor, last_timestamp, document["name"])]

        members = []
        if "members" in document:
            members = document["members"]

        admin_users = yield Query(self.database, 'Users').find({'role': 'administrator'})
        admin_emails = [admin_user["username"] for admin_user in admin_users]
        members = list(set(members + admin_emails))

        namespace["members"] = members
        namespace = yield Query(self.database, "Namespaces").update(namespace)

        raise Return(namespace)

    @coroutine
    def update(self, document):
        logging.debug("Updating namespace %s", document["_id"])

        initial_namespace = yield Query(self.database, "Namespaces").find_one({"_id": document['_id']})
        if not initial_namespace:
            raise ObjectNotFoundError("Namespace %s not found." % document["_id"])

        # TODO: validate members before inserting and do an intersection for race conditions
        namespace = dict(initial_namespace)
        namespace["members"] = document["members"]
        updated_namespace = yield Query(self.database, "Namespaces").update(namespace)

        raise Return((initial_namespace, updated_namespace))

    @coroutine
    def delete(self, document):
        logging.info("Deleting namespace %s", document)

        response = yield self.kube.namespaces.delete(document["name"])
        raise Return(response)

    @coroutine
    def create_notifications(self, operation, body_request, document, initial_document=None):
        if operation == "create":
            yield notifications.add_notification(
                self.database,
                user=self.user,
                operation=operation,
                resource=document["name"],
                subject="created Namespace %s" % document["name"],
                kind="Namespace"
            )
        elif operation == "update":
            members_added = self._diff(document.get("members", []), initial_document.get("members", []))
            members_removed = self._diff(initial_document.get("members", []), document.get("members", []))

            subject = ''
            if len(members_added) > 0:
                subject = "added %s members" % ','.join(members_added)

            if len(members_removed) > 0:
                if subject != '':
                    subject += 'and removed %s members to namespace %s' % (','.join(members_removed), document["name"])
                else:
                    subject = 'removed %s members to namespace %s' % (','.join(members_removed), document["name"])

            yield notifications.add_notification(
                self.database,
                user=self.user,
                operation=operation,
                resource=document["name"],
                subject=subject,
                kind="Namespace",
                namespace=document["name"]
            )

    @coroutine
    def _wait_namespace_creation(self, cursor, last_timestamp, name):
        while True:
            if not cursor.alive:
                cursor = self.oplog.find({
                    "ts": {"$gt": last_timestamp},
                    "op": {"$in": ["i"]},
                    "ns": {"$in": ["elastickube.Namespaces"]}
                }, cursor_type=pymongo.CursorType.TAILABLE_AWAIT)

                cursor.add_option(8)
                logging.debug("Tailable cursor recreated.")

            if (yield cursor.fetch_next):
                document = cursor.next_object()
                last_timestamp = document["ts"]
                if document["o"]["name"] == name:
                    break

        raise Return(document["o"])

    def _diff(self, a, b):
        b = set(b)
        return [item for item in a if item not in b]
