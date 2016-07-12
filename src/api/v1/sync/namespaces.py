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

from tornado.gen import coroutine
from tornado.httpclient import HTTPError

from data.query import Query


class SyncNamespaces(object):

    def __init__(self, settings):
        logging.info("Initializing SyncNamespaces")

        self.settings = settings
        self.resource_version = None

    @staticmethod
    def _convert_namespace(kube_namespace):
        labels = dict()
        if "labels" in kube_namespace["metadata"]:
            labels = kube_namespace["metadata"]["labels"]

        return dict(
            _id=kube_namespace["metadata"]["uid"],
            name=kube_namespace["metadata"]["name"],
            metadata=dict(
                name=kube_namespace["metadata"]["name"],
                labels=labels,
                uid=kube_namespace["metadata"]["uid"]
            )
        )

    @coroutine
    def _update_namespace(self, namespace):
        update = {
            "metadata.name": namespace["metadata"]["name"],
            "metadata.labels": namespace["metadata"]["labels"]
        }

        yield Query(self.settings["database"], "Namespaces").update_fields({"_id": namespace["_id"]}, update)

    @coroutine
    def _add_admin_users(self, namespace):
        admin_users = yield Query(self.settings["database"], "Users").find({"role": "administrator"})
        namespace["members"] = [admin_user["username"] for admin_user in admin_users]

    @coroutine
    def start_sync(self):
        @coroutine
        def data_callback(data):
            logging.debug("Calling data_callback for SyncNamespaces")

            self.resource_version = data["object"]["metadata"]["resourceVersion"]

            converted_namespace = self._convert_namespace(data["object"])
            if data["type"] == "ADDED":
                yield self._add_admin_users(converted_namespace)
                yield Query(self.settings["database"], "Namespaces").insert(converted_namespace)

            elif data["type"] == "DELETED":
                yield Query(self.settings["database"], "Namespaces").remove(converted_namespace)

            else:
                yield self._update_namespace(converted_namespace)

        def done_callback(future):
            logging.warn("Disconnected from kubeclient in SyncNamespaces")

            if future and future.exception():
                logging.exception(future.exception())

                if isinstance(future.exception(), HTTPError) and future.exception().code == 599:
                    logging.debug("Reconnecting to kubeclient in SyncNamespaces on 599 error code")
                    self.settings["kube"].namespaces.watch(
                        resourceVersion=self.resource_version,
                        on_data=data_callback).add_done_callback(done_callback)
            else:
                logging.debug("Reconnecting to kubeclient in SyncNamespaces")
                self.settings["kube"].namespaces.watch(
                    resourceVersion=self.resource_version,
                    on_data=data_callback).add_done_callback(done_callback)

        logging.info("start_sync SyncNamespaces")

        existing_namespaces = yield Query(self.settings["database"], "Namespaces").find(projection=["_id"])
        namespace_ids = [namespace["_id"] for namespace in existing_namespaces]

        result = yield self.settings["kube"].namespaces.get()
        for item in result.get("items", []):
            namespace = self._convert_namespace(item)
            if namespace["_id"] in namespace_ids:
                yield self._update_namespace(namespace)
            else:
                yield self._add_admin_users(namespace)
                yield Query(self.settings["database"], "Namespaces").insert(namespace)

        self.resource_version = result["metadata"]["resourceVersion"]
        self.settings["kube"].namespaces.watch(
            on_data=data_callback,
            resourceVersion=self.resource_version).add_done_callback(done_callback)
