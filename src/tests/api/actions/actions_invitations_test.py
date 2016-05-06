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

import json
import logging
import uuid

from pymongo import MongoClient
from tornado import testing
from tornado.httpclient import AsyncHTTPClient
from tornado.websocket import websocket_connect

from tests.api import wait_message, get_ws_request, get_api_address, validate_response

ELASTICKUBE_VALIDATION_TOKEN_HEADER = "ElasticKube-Validation-Token"


class ActionsInvitationsTests(testing.AsyncTestCase):

    _multiprocess_can_split_ = True

    @staticmethod
    def _delete_user(email):
        database = MongoClient("mongodb://%s:27017/" % get_api_address()).elastickube
        database.Users.remove({"email": email})

    @testing.gen_test(timeout=60)
    def test_create_invitations(self):
        logging.debug("Start test_create_invitations")

        user_email = "test_%s@elasticbox.com" % str(uuid.uuid4())[:10]
        self.addCleanup(self._delete_user, user_email)

        request = yield get_ws_request(self.io_loop)
        connection = yield websocket_connect(request)

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "invitations",
            "operation": "create",
            "correlation": correlation,
            "body": {
                "emails": [user_email],
                "note": "Test note"
            }
        }))

        message = yield wait_message(connection, correlation)
        validate_response(
            self,
            message,
            dict(status_code=200, correlation=correlation, operation="created", action="invitations"))

        database = MongoClient("mongodb://%s:27017/" % get_api_address()).elastickube
        user = database.Users.find_one({"email": user_email})

        invitation_token = user["invite_token"]

        data = dict(email=user_email, password="elastickube123", firstname="firstname", lastname="lastname")
        yield AsyncHTTPClient(self.io_loop).fetch(
            "http://%s/api/v1/auth/signup" % get_api_address(),
            method='POST',
            headers={ELASTICKUBE_VALIDATION_TOKEN_HEADER: invitation_token},
            body=json.dumps(data))

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "users",
            "operation": "watch",
            "correlation": correlation
        }))

        message = yield wait_message(connection, correlation)
        new_user = None
        for user in message["body"]:
            if user["email"] == user_email:
                new_user = user
                break

        self.assertIsNotNone(new_user)

        connection.close()
        logging.debug("Completed test_create_invitations")

    @testing.gen_test(timeout=60)
    def test_update_invitations(self):
        logging.debug("Start test_update_invitations")

        request = yield get_ws_request(self.io_loop)
        connection = yield websocket_connect(request)

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "invitations",
            "operation": "update",
            "correlation": correlation,
            "body": dict()
        }))

        message = yield wait_message(connection, correlation)
        validate_response(
            self,
            message,
            dict(status_code=405, correlation=correlation, operation="update", action="invitations", body_type=dict))
        expected_message = "Operation update not supported for action invitations."
        self.assertTrue(message["body"]["message"] == expected_message,
                        "Message is %s instead of '%s'" % (message["body"]["message"], expected_message))

        connection.close()
        logging.debug("Completed test_update_invitations")

    @testing.gen_test(timeout=60)
    def test_delete_invitations(self):
        logging.debug("Start test_delete_invitations")

        request = yield get_ws_request(self.io_loop)
        connection = yield websocket_connect(request)

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "invitations",
            "operation": "delete",
            "correlation": correlation,
            "body": dict()
        }))

        message = yield wait_message(connection, correlation)
        validate_response(
            self,
            message,
            dict(status_code=405, correlation=correlation, operation="delete", action="invitations", body_type=dict))
        expected_message = "Operation delete not supported for action invitations."
        self.assertTrue(message["body"]["message"] == expected_message,
                        "Message is %s instead of '%s'" % (message["body"]["message"], expected_message))

        connection.close()
        logging.debug("Completed test_delete_invitations")

    @testing.gen_test(timeout=60)
    def test_invite_unauthorized(self):
        logging.debug("Start test_invite_unauthorized")

        request = yield get_ws_request(self.io_loop, username="engineer@elasticbox.com")
        connection = yield websocket_connect(request)

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "invitations",
            "operation": "create",
            "correlation": correlation,
            "body": dict()
        }))

        message = yield wait_message(connection, correlation)
        validate_response(
            self,
            message,
            dict(status_code=403, correlation=correlation, operation="create", action="invitations", body_type=dict))

        expected_message = "Operation create forbidden for action invitations."
        self.assertTrue(message["body"]["message"] == expected_message,
                        "Message is %s instead of '%s'" % (message["body"]["message"], expected_message))

        connection.close()
        logging.debug("Completed test_invite_unauthorized")


if __name__ == "__main__":
    testing.main()
