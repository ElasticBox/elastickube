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


class MessageValidationTest(testing.AsyncTestCase):

    @testing.gen_test(timeout=60)
    def test_message_validation(self):
        logging.debug("Start test_message_validation")

        token = yield get_token(self.io_loop)
        request = HTTPRequest(
            "ws://%s/api/v1/ws" % get_api_address(),
            headers=dict([(ELASTICKUBE_TOKEN_HEADER, token)]),
            validate_cert=False
        )

        connection = yield websocket_connect(request)

        connection.write_message("No JSON object")
        message = yield connection.read_message()
        self.assertTrue(message == '"Message \'No JSON object\' cannot be deserialized"',
                        "Received %s instead of '\"Message 'No JSON object' cannot be deserialized\"'" % message)

        connection.write_message(json.dumps({
            "operation": "create",
            "correlation": 123
        }))

        message = yield connection.read_message()
        expected_message = "\"Message {\\\"operation\\\": \\\"create\\\", \\\"correlation\\\": 123}"\
            " does not contain 'action'\""
        self.assertTrue(message == expected_message, "Received %s instead of '%s'" % (message, expected_message))

        connection.write_message(json.dumps({
            "action": "users",
            "correlation": 123
        }))

        message = yield connection.read_message()
        expected_message = "\"Message {\\\"action\\\": \\\"users\\\", \\\"correlation\\\": 123}" \
                           " does not contain 'operation'\""
        self.assertTrue(message == expected_message, "Received %s instead of '%s'" % (message, expected_message))

        connection.write_message(json.dumps({
            "action": "users",
            "operation": "create"
        }))

        message = yield connection.read_message()
        expected_message = "\"Message {\\\"action\\\": \\\"users\\\", \\\"operation\\\": \\\"create\\\"}" \
                           " does not contain 'correlation'\""
        self.assertTrue(message == expected_message, "Received %s instead of '%s'" % (message, expected_message))

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "fake_action",
            "operation": "create",
            "correlation": correlation
        }))

        deserialized_message = yield wait_message(connection, correlation)
        self.assertTrue(deserialized_message['status_code'] == 400,
                        "Status code is %d instead of 400" % deserialized_message['status_code'])
        self.assertTrue(deserialized_message['correlation'] == correlation,
                        "Correlation is %s instead of %s" % (deserialized_message["correlation"], correlation))
        self.assertTrue(deserialized_message['operation'] == "create",
                        "Operation is %s instead of create" % deserialized_message['operation'])
        self.assertTrue(deserialized_message['action'] == "fake_action",
                        "Action is %s instead of fake_action" % deserialized_message['action'])
        self.assertTrue(isinstance(deserialized_message['body'], dict),
                        "Body is not a dict but %s" % type(deserialized_message['body']))

        expected_message = "Action fake_action not supported."
        self.assertTrue(deserialized_message["body"]["message"] == expected_message,
                        "Message is %s instead of '%s'" % (deserialized_message['body']["message"], expected_message))

        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "users",
            "operation": "fake_operation",
            "correlation": correlation
        }))

        deserialized_message = yield wait_message(connection, correlation)
        self.assertTrue(deserialized_message['status_code'] == 400,
                        "Status code is %d instead of 400" % deserialized_message['status_code'])
        self.assertTrue(deserialized_message['correlation'] == correlation,
                        "Correlation is %s instead of %s" % (deserialized_message["correlation"], correlation))
        self.assertTrue(deserialized_message['operation'] == "fake_operation",
                        "Operation is %s instead of fake_operation" % deserialized_message['operation'])
        self.assertTrue(deserialized_message['action'] == "users",
                        "Action is %s instead of users" % deserialized_message['action'])
        self.assertTrue(isinstance(deserialized_message['body'], dict),
                        "Body is not a dict but %s" % type(deserialized_message['body']))

        expected_message = "Operation fake_operation not supported."
        self.assertTrue(deserialized_message["body"]["message"] == expected_message,
                        "Message is %s instead of '%s'" % (deserialized_message['body']["message"], expected_message))

        connection.close()
        logging.debug("Completed test_message_validation")


if __name__ == '__main__':
    testing.main()
