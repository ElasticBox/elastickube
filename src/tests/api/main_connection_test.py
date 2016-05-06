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

from tests.api import ELASTICKUBE_TOKEN_HEADER, get_api_address


class MainConnectionTest(testing.AsyncTestCase):

    _multiprocess_can_split_ = True

    @testing.gen_test(timeout=60)
    def test_main_connection(self):
        logging.debug("Start test_main_connection")

        request = HTTPRequest(
            "ws://%s/api/v1/ws" % get_api_address(),
            headers=dict([(ELASTICKUBE_TOKEN_HEADER, 'fake_token')]),
            validate_cert=False
        )

        connection = yield websocket_connect(request)
        correlation = str(uuid.uuid4())[:10]
        connection.write_message(json.dumps({
            "action": "charts",
            "operation": "watch",
            "correlation": correlation
        }))

        deserialized_message = None
        while True:
            message = yield connection.read_message()
            deserialized_message = json.loads(message)
            if deserialized_message:
                break

        self.assertTrue(isinstance(deserialized_message, dict),
                        "Body is not a dict but %s" % type(deserialized_message))
        expected_message = "Invalid token."
        self.assertTrue(deserialized_message["error"]["message"] == expected_message,
                        "Message is %s instead of '%s'" % (deserialized_message["error"]["message"], expected_message))
        connection.close()

        logging.debug("Completed test_main_connection")


if __name__ == "__main__":
    testing.main()
