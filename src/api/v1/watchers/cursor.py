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

from inspect import isfunction, isgeneratorfunction
from tornado.gen import coroutine, Return

from api.v1.watchers.metadata import WatcherMetadata
from data.query import Query
from data.watch import add_callback, remove_callback


class CursorWatcher(object):

    def __init__(self, message, settings, user, callback):
        logging.info("Initializing CursorWatcher")

        self._params = dict()

        self.callback = callback
        self.message = message
        self.settings = settings
        self.user = user

        self.metadata = WatcherMetadata(self.message["action"]).get(settings)
        self.validate_message()

    @coroutine
    def watch(self):
        logging.info("Starting watch for collection %s", self.metadata["collection"])

        if isfunction(self.metadata["criteria"]):
            criteria = yield self.metadata["criteria"](self.user, self.message, self.settings)
        else:
            criteria = self.metadata["criteria"]

        data = yield Query(
            self.settings["database"],
            self.metadata["collection"],
            manipulate=self.metadata["manipulate"]).find(
                criteria=criteria,
                projection=self.metadata["projection"],
                sort=self.metadata["sort"],
                limit=self.metadata["limit"])

        data = yield self.filter_data(data)
        self.callback(dict(
            action=self.message["action"],
            operation="watched",
            correlation=self.message["correlation"],
            status_code=200,
            body=data
        ))

        add_callback(self.metadata["collection"], self.data_callback)

    @coroutine
    def data_callback(self, document):
        logging.info("CursorWatcher for collection %s data_callback (%s)", self.metadata["collection"], document["op"])

        operation = "updated"
        if document["op"] == "i":
            operation = "created"
        elif document["op"] == "d":
            operation = "deleted"

        if self.metadata["projection"]:
            for key in self.metadata["projection"].iterkeys():
                if key in document["o"]:
                    del document["o"][key]

        data = yield self.filter_data(document["o"])
        yield self.callback(dict(
            action=self.message["action"],
            operation=operation,
            status_code=200,
            body=data
        ))

        raise Return()

    def unwatch(self):
        logging.info("Stopping watch for collection %s", self.metadata["collection"])
        remove_callback(self.metadata["collection"], self.data_callback)

    @coroutine
    def filter_data(self, data):
        if self.metadata["filter_data"]:
            data = yield self.metadata["filter_data"](data, self.user, self.message, self.settings)

        raise Return(data)

    @coroutine
    def check_permissions(self, operation, _document):
        logging.debug("check_permissions for user %s and operation %s on db watch", self.user["username"], operation)
        raise Return(True)

    def validate_message(self):
        if not self.metadata:
            self.callback(dict(
                action=self.message["action"],
                operation=self.message["operation"],
                correlation=self.message["correlation"],
                body={"message": "Action %s not supported by CursorWatcher" % self.message["action"]},
                status_code=400
            ))

            raise RuntimeError()
