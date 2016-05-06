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

from tornado import testing
from tornado.httpclient import HTTPRequest
from tornado.websocket import websocket_connect

from tests.api import get_token, wait_message, get_api_address, ELASTICKUBE_TOKEN_HEADER


class WatchUsersTest(testing.AsyncTestCase):

    _multiprocess_can_split_ = True

    @testing.gen_test(timeout=60)
    def test_watch_users(self):
        logging.debug("Start test_watch_users")

        token = yield get_token(self.io_loop)
        request = HTTPRequest(
            "ws://%s/api/v1/ws" % get_api_address(),
            headers=dict([(ELASTICKUBE_TOKEN_HEADER, token)]),
            validate_cert=False
        )

        connection = yield websocket_connect(request)

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "users",
            "operation": "watch",
            "correlation": correlation
        }))

        deserialized_message = yield wait_message(connection, correlation)
        self.assertTrue(deserialized_message["status_code"] == 200,
                        "Status code is %d instead of 200" % deserialized_message["status_code"])
        self.assertTrue(deserialized_message["correlation"] == correlation,
                        "Correlation is %s instead of %s" % (deserialized_message["correlation"], correlation))
        self.assertTrue(deserialized_message["operation"] == "watched",
                        "Operation is %s instead of watched" % deserialized_message["operation"])
        self.assertTrue(deserialized_message["action"] == "users",
                        "Action is %s instead of users" % deserialized_message["action"])
        self.assertTrue(isinstance(deserialized_message["body"], list),
                        "Body is not a list but %s" % type(deserialized_message["body"]))
        self.assertTrue(len(deserialized_message["body"]) > 0, "No users returned as part of the response")

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "users",
            "operation": "watch",
            "correlation": correlation
        }))

        deserialized_message = yield wait_message(connection, correlation)
        self.assertTrue(deserialized_message["status_code"] == 400,
                        "Status code is %d instead of 400" % deserialized_message["status_code"])
        self.assertTrue(deserialized_message["correlation"] == correlation,
                        "Correlation is %s instead of %s" % (deserialized_message["correlation"], correlation))
        self.assertTrue(deserialized_message["operation"] == "watched",
                        "Operation is %s instead of watched" % deserialized_message["operation"])
        self.assertTrue(deserialized_message["action"] == "users",
                        "Action is %s instead of users" % deserialized_message["action"])
        self.assertTrue(isinstance(deserialized_message["body"], dict),
                        "Body is not a dict but %s" % type(deserialized_message["body"]))
        self.assertTrue(deserialized_message["body"]["message"] == "Action already watched.",
                        "Message is %s instead of 'Action already watched.'" % deserialized_message["body"]["message"])

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "users",
            "operation": "unwatch",
            "correlation": correlation
        }))

        deserialized_message = yield wait_message(connection, correlation)
        self.assertTrue(deserialized_message['status_code'] == 200,
                        "Status code is %d instead of 200" % deserialized_message['status_code'])
        self.assertTrue(deserialized_message["correlation"] == correlation,
                        "Correlation is %s instead of %s" % (deserialized_message["correlation"], correlation))
        self.assertTrue(deserialized_message['operation'] == "unwatched",
                        "Operation is %s instead of unwatched" % deserialized_message['operation'])
        self.assertTrue(deserialized_message['action'] == "users",
                        "Action is %s instead of users" % deserialized_message['action'])
        self.assertTrue(isinstance(deserialized_message['body'], dict),
                        "Body is not a dict but %s" % type(deserialized_message['body']))
        self.assertTrue(len(deserialized_message['body'].keys()) == 0, "Body is not empty")

        connection.close()
        logging.debug("Completed test_watch_users")


if __name__ == '__main__':
    testing.main()
