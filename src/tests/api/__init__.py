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

import os
import json

from tornado.gen import coroutine, Return
from tornado.httpclient import AsyncHTTPClient, HTTPRequest

ELASTICKUBE_TOKEN_HEADER = "ElasticKube-Token"


@coroutine
def get_token(io_loop, username="operations@elasticbox.com", password="elastickube123"):
    response = yield AsyncHTTPClient(io_loop).fetch(
        "http://%s/api/v1/auth/login" % get_api_address(),
        method="POST",
        body=json.dumps(dict(username=username, password=password)))

    raise Return(response.body)


@coroutine
def get_ws_request(io_loop, username="operations@elasticbox.com", password="elastickube123"):
    token = yield get_token(io_loop, username, password)
    request = HTTPRequest(
        "ws://%s/api/v1/ws" % get_api_address(),
        headers=dict([(ELASTICKUBE_TOKEN_HEADER, token)]),
        validate_cert=False
    )

    raise Return(request)


@coroutine
def wait_message(connection, correlation):
    deserialized_message = None
    while True:
        message = yield connection.read_message()
        deserialized_message = json.loads(message)
        if "correlation" in deserialized_message and deserialized_message["correlation"] == correlation:
            break

    raise Return(deserialized_message)


def get_api_address():
    return os.getenv("ELASTICKUBE_API_ADDRESS", "localhost")


def validate_response(test_case, message, expected_result):
    test_case.assertTrue(message["status_code"] == expected_result["status_code"],
                         "Status code is %d instead of %d" % (message["status_code"], expected_result["status_code"]))
    test_case.assertTrue(message["correlation"] == expected_result["correlation"],
                         "Correlation is %s instead of %s" % (message["correlation"], expected_result["correlation"]))
    test_case.assertTrue(message["operation"] == expected_result["operation"],
                         "Operation is %s instead of %s" % (message["operation"], expected_result["operation"]))
    test_case.assertTrue(message["action"] == expected_result["action"],
                         "Action is %s instead of %s" % (message["action"], expected_result["action"]))

    if "body_type" in expected_result:
        test_case.assertTrue(isinstance(message["body"], expected_result["body_type"]),
                             "Body is not a %s but %s" % (expected_result["body_type"], type(message["body"])))
    else:
        test_case.assertIsNone(message["body"], "Body is not a None but '%s'" % message["body"])
