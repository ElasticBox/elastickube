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
