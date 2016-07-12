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

from tornado.gen import coroutine, Return


class LogsActions(object):

    def __init__(self, settings, user):
        logging.info("Initializing LogsActions")

        self.kube = settings["kube"]
        self.database = settings["database"]
        self.user = user
        self.notifications = []

    @coroutine
    def check_permissions(self, operation, _request_body):
        logging.debug("check_permissions for user %s and operation %s on instances", self.user["username"], operation)
        raise Return(True)

    @coroutine
    def retrieve(self, document):
        logging.debug("Retrieving logs for request %s", document)

        logs = yield self.kube.pods.log(**document)
        raise Return(logs)
