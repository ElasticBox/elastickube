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

from bson.objectid import ObjectId
from tornado.gen import coroutine, Return

from data.query import Query


class NotificationsActions(object):

    def __init__(self, settings, user):
        logging.info("Initializing NotificationsActions")

        self.kube = settings["kube"]
        self.database = settings["database"]
        self.user = user

    @coroutine
    def check_permissions(self, operation, _document):
        logging.debug("check_permissions for user %s and operation %s on notifications", self.user["username"], operation)
        raise Return(True)

    @coroutine
    def retrieve(self, document):
        logging.debug("Retrieving older notifications from %s", document)

        criteria = yield self._criteria_older_notifications(document)
        notifications = yield Query(self.database, "Notifications").find(
            criteria=criteria,
            sort=[("metadata.creationTimestamp", pymongo.DESCENDING)],
            limit=document.get('pageSize', 10)
        )

        raise Return(notifications)

    @coroutine
    def update(self, document):
        logging.debug("Updating user notifications info with %s", document)

        user = yield Query(self.database, "Users").find_one({"_id": ObjectId(self.user['_id'])})
        if not user:
            raise ObjectNotFoundError("User %s not found." % document["_id"])

        if "viewed_at" in document and user.get("notifications_viewed_at", 0) < document["viewed_at"]:
            user["notifications_viewed_at"] = document["viewed_at"]
            yield Query(self.database, "Users").update(user)

        elif "email_notifications" in document:
            if "notifications" not in user:
                user["notifications"] = {}

            user["notifications"]["namespace"] = bool(document["email_notifications"])
            yield Query(self.database, "Users").update(user)

        raise Return(True)

    @coroutine
    def _criteria_older_notifications(self, document):
        criteria = {
            "metadata.creationTimestamp": {
                "$lt": document["lastNotification"]["metadata"]["creationTimestamp"]
            }
        }

        if self.user["role"] != "administrator":
            namespaces = yield Query(self.database, "Namespaces").find(
                criteria={"members": self.user["username"]},
                projection=["name"])

            criteria = {'$and': [
                criteria,
                {"namespace": {'$in': [n["name"] for n in namespaces]}}
            ]}

        raise Return(criteria)


@coroutine
def add_notification(database, user, operation, resource, kind, namespace=None):
    notification = {
        "user": user,
        "operation": operation,
        "resource": {
            "kind": kind,
            "name": resource
        }
    }
    if namespace is not None:
        notification["namespace"] = namespace

    yield Query(database, "Notifications").insert(notification)


def generate_notifications_template(origin_user, invite_address, message):
    # message_escaped = cgi.escape(message)  # Message must be unicode and escaped
    # name_escaped = cgi.escape(origin_user['name'])
    # email_escaped = cgi.escape(origin_user['email'], quote=True)
    # invite_address_escaped = cgi.escape(invite_address)

    return NOTIFICATIONS_TEMPLATE
    # return NOTIFICATIONS_TEMPLATE.format(invite_address=invite_address_escaped, custom_message=message_escaped,
    #                               origin_name=name_escaped, origin_email=email_escaped)


def send_notifications_sync(smtp_config, origin_user, users, message):
    try:
        for user in users:
            template = generate_notifications_template(origin_user, invite['confirm_url'], message)
            send(smtp_config, user['email'], NOTIFICATIONS_SUBJECT, template, HTML_BODY_TYPE)
    except Exception:
        logging.exception("Exception detected sending notifications")
        raise


@coroutine
def send_notifications(smtp_config, origin_user, info_users, message, threadpool=None):
    if threadpool is None:
        threadpool = DEFAULT_THREADPOOL

    result = yield threadpool.submit(send_notifications_sync, smtp_config, origin_user, info_users, message)
    raise Return(result)
