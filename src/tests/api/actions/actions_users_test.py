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

from bson.objectid import ObjectId
from motor.motor_tornado import MotorClient
from tornado import testing
from tornado.websocket import websocket_connect

from tests.api import get_ws_request, validate_response, wait_message, get_api_address


class ActionsUsersTests(testing.AsyncTestCase):

    _multiprocess_can_split_ = True

    def setUp(self):
        super(ActionsUsersTests, self).setUp()

        self.user_id = None
        self.user_email = "test_%s@elasticbox.com" % str(uuid.uuid4())[:10]

    def tearDown(self):
        if self.user_id:
            self._delete_user()

        super(ActionsUsersTests, self).tearDown()

    @testing.gen_test
    def _delete_user(self):
        database = MotorClient("mongodb://%s:27017/" % get_api_address()).elastickube
        yield database.Users.remove({"_id": ObjectId(self.user_id)})

    @testing.gen_test(timeout=60)
    def test_create_user(self):
        logging.debug("Start test_create_user")

        request = yield get_ws_request(self.io_loop)
        connection = yield websocket_connect(request)

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "users",
            "operation": "create",
            "correlation": correlation,
            "body": dict()
        }))

        message = yield wait_message(connection, correlation)
        validate_response(
            self,
            message,
            dict(status_code=405, correlation=correlation, operation="create", action="users", body_type=dict))

        logging.debug("Completed test_create_user")


if __name__ == "__main__":
    testing.main()
