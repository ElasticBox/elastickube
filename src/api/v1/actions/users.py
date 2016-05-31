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
from datetime import datetime

from bson.objectid import ObjectId
from tornado.gen import coroutine, Return

from data.query import Query, ObjectNotFoundError


class UsersActions(object):

    def __init__(self, settings, user):
        logging.info("Initializing UsersActions")

        self.database = settings['database']
        self.user = user

    @coroutine
    def check_permissions(self, operation, document):
        logging.debug("check_permissions for user %s and operation %s on users", self.user["username"], operation)
        if operation in ["create", "delete"] and self.user["role"] != "administrator":
            raise Return(False)

        if operation == "update" and str(self.user["_id"]) != document["_id"] and self.user["role"] != "administrator":
            raise Return(False)

        if (operation == "update" and
                self.user["_id"] == document["_id"] and
                self.user["role"] == "user" and
                self.user["role"] != document["role"]):
            raise Return(False)

        raise Return(True)

    @coroutine
    def update(self, document):
        logging.debug("Updating user %s", document["_id"])

        user = yield Query(self.database, "Users").find_one({"_id": ObjectId(document['_id'])})
        if not user:
            raise ObjectNotFoundError("User %s not found." % document["_id"])

        user.update(document)
        updated_user = yield Query(self.database, "Users").update(user)
        raise Return(updated_user)

    @coroutine
    def delete(self, document):
        logging.info("Deleting user %s", document["_id"])

        user = yield Query(self.database, "Users").find_one({"_id": ObjectId(document["_id"])})
        if user is not None:
            user["metadata"]["deletionTimestamp"] = datetime.utcnow().isoformat()
            yield Query(self.database, "Users").update(user)

            notification = {
                "user": self.user["username"],
                "operation": "delete",
                "resource": {
                    "kind": "User",
                    "name": document["username"]
                }
            }
            yield Query(self.database, "Notifications").insert(notification)
        else:
            raise ObjectNotFoundError("User %s not found." % document["_id"])
