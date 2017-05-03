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

from pymongo import DESCENDING
from tornado.gen import coroutine, Return

from data.query import Query, ObjectNotFoundError


class NotificationsActions(object):

    def __init__(self, settings, user):
        logging.info("Initializing NotificationsActions")

        self.database = settings["database"]
        self.user = user
        self.notifications = []

    @coroutine
    def check_permissions(self, operation, _request_body):
        logging.debug(
            "check_permissions for user %s and operation %s on notifications", self.user["username"], operation)
        raise Return(True)

    @coroutine
    def retrieve(self, document):
        logging.debug('Retrieving notifications for request %s', document)

        criteria = {
            "user": self.user["username"],
            "unread": True
        }

        if "all" in document and document["all"]:
            del criteria["unread"]

        if "before" in document:
            criteria["metadata.creationTimestamp"] = {
                "$lt": document["before"]
            }

        notifications = yield Query(self.database, 'Notifications').find(
            criteria=criteria,
            sort=[('metadata.creationTimestamp', DESCENDING)],
            limit=document.get('pageSize', 10)
        )

        raise Return(notifications)

    @coroutine
    def update(self, document):
        logging.debug("Updating notifications %s", document["_id"])

        initial_notification = yield Query(self.database, "Notifications").find_one({"_id": document['_id']})
        if not initial_notification:
            raise ObjectNotFoundError("Notification %s not found." % document["_id"])

        initial_notification["unread"] = document["unread"]
        updated_notification = yield Query(self.database, "Notifications").update(initial_notification)

        raise Return((initial_notification, updated_notification))


@coroutine
def add_notification(database, user, operation, resource, kind, subject, namespace=None):
    if namespace:
        full_namespace = yield Query(database, 'Namespaces').find_one({'name': namespace})
        namespace_members = full_namespace["members"]
        target_users = yield Query(database, 'Users').find(
            {"username": {"$in": namespace_members}},
            {"notifications.namespace": True})
    else:
        admin_users = yield Query(database, 'Users').find({'role': 'administrator'})
        target_users = [admin_user["username"] for admin_user in admin_users]

    notification = {
        "trigger": user["username"],
        "operation": operation,
        "resource": {
            "kind": kind,
            "name": resource
        },
        "subject": subject,
        "unread": True,
        "schema": "http://elasticbox.net/schemas/notification"
    }

    if namespace is not None:
        notification["resource"]["namespace"] = namespace

    notifications = []
    for target_user in target_users:
        target_notification = dict(notification)
        target_notification["user"] = target_user
        notifications.append(target_notification)

    yield Query(database, "Notifications").insert_bulk(notifications)
