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

import uuid

import unittest2
from pymongo import MongoClient
from tornado import testing

from tests import api


class TestActionsSettings(api.ApiTestCase):

    def _delete_user(self, email):
        database = MongoClient("mongodb://%s:27017/" % self.get_api_address()).elastickube
        database.Users.remove({"email": email})

    @testing.gen_test(timeout=60)
    def test_create_namespace(self):
        namespace_name = "test-%s" % str(uuid.uuid4())[:4]

        correlation = self.send_message("namespaces", "create", body=dict(name=namespace_name))
        response = yield self.wait_message(self.connection, correlation)
        self.validate_response(response, 200, correlation, "created", "namespaces")
        self.assertTrue(isinstance(response["body"], dict), "Body is not a dict but %s" % type(response["body"]))

        correlation = self.send_message("notifications", "retrieve")
        response = yield self.wait_message(self.connection, correlation)
        self.validate_response(response, 200, correlation, "retrieved", "notifications")
        self.assertTrue(isinstance(response["body"], list), "Body is not a list but %s" % type(response["body"]))
        self.assertTrue(len(response["body"]) > 0, "Body does not have notifications")

        current_notification = None
        all_notifications = response["body"]
        for notification in all_notifications:
            if notification["resource"]["name"] == namespace_name:
                current_notification = notification
                break

        self.assertIsNotNone(current_notification, "No notification created.")
        self.assertIsNotNone(current_notification["unread"], "Unread flag incorrect value")

        current_notification["unread"] = False
        correlation = self.send_message("notifications", "update", body=current_notification)
        response = yield self.wait_message(self.connection, correlation)
        self.validate_response(response, 200, correlation, "updated", "notifications")
        self.assertTrue(isinstance(response["body"], dict), "Body is not a list but %s" % type(response["body"]))

        correlation = self.send_message("namespaces", "delete", body=dict(name=namespace_name))
        response = yield self.wait_message(self.connection, correlation)
        self.validate_response(response, 200, correlation, "deleted", "namespaces")


if __name__ == "__main__":
    unittest2.main()
