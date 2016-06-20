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

import httplib
import logging

from bson.json_util import loads
from pymongo.errors import DuplicateKeyError, PyMongoError
from tornado.gen import coroutine, Return, Future

from api.kube.exceptions import KubernetesException
from api.v1 import SecureWebSocketHandler
from api.v1.actions.logs import LogsActions
from api.v1.actions.instances import InstancesActions
from api.v1.actions.namespaces import NamespacesActions
from api.v1.actions.notifications import NotificationsActions
from api.v1.actions.settings import SettingsActions
from api.v1.actions.users import UsersActions
from api.v1.actions.invitations import InvitationsActions
from api.v1.watchers.cursor import CursorWatcher
from api.v1.watchers.kube import KubeWatcher
from api.v1.watchers.metrics import MetricsWatcher
from data.query import ObjectNotFoundError

REST_OPERATIONS = ["retrieve", "create", "update", "delete"]
WATCH_OPERATIONS = ["watch", "unwatch"]
SUPPORTED_ACTIONS = [
    "users",
    "settings",
    "namespaces",
    "instances",
    "instance",
    "invitations",
    "charts",
    "logs",
    "metrics",
    "notifications"
]


class MainWebSocketHandler(SecureWebSocketHandler):

    def __init__(self, application, request, **kwargs):
        super(MainWebSocketHandler, self).__init__(application, request, **kwargs)

        self.actions_lookup = None
        self.connected = False
        self.current_watchers = dict()

    def open(self):
        logging.info("Initializing MainWebSocketHandler")
        super(MainWebSocketHandler, self).open()

    @coroutine
    def on_message(self, message):
        # Wait the user to be authenticated before accepting message
        if isinstance(self.user, Future):
            self.user = yield self.user
            self.build_actions_lookup()

        if not self.user:
            self.write_message({"error": {"message": "Invalid token."}})
            self.close(httplib.UNAUTHORIZED, "Invalid token.")
            raise Return()

        request = yield self.validate_message(message)
        if not request:
            raise Return()

        response = dict(
            action=request["action"],
            correlation=request["correlation"],
            operation=request["operation"],
            body={},
            status_code=200
        )

        body = request["body"] if "body" in request else dict()
        if request["operation"] in REST_OPERATIONS:
            action = self.actions_lookup[request["action"]].get("rest", None)
            if action:
                if (not hasattr(type(action), request["operation"]) or
                        not callable(getattr(type(action), request["operation"]))):
                    error = "Operation %s not supported for action %s." % (request["operation"], request["action"])
                    response.update(dict(status_code=405, body=dict(message=error)))

                else:
                    if not (yield action.check_permissions(request["operation"], body)):
                        error = "Operation %s forbidden for action %s." % (request["operation"], request["action"])
                        response.update(dict(status_code=403, body=dict(message=error)))

                    else:
                        try:
                            if request["operation"] == "retrieve":
                                response["body"] = yield action.retrieve(body)
                                response["operation"] = "retrieved"

                            elif request["operation"] == "create":
                                response["body"] = yield action.create(body)
                                response["operation"] = "created"

                            elif request["operation"] == "update":
                                response["body"] = yield action.update(body)
                                response["operation"] = "updated"

                            elif request["operation"] == "delete":
                                response["body"] = yield action.delete(body)
                                response["operation"] = "deleted"

                        except PyMongoError as pymongo_error:
                            response["body"] = dict(message=pymongo_error.message)
                            if isinstance(pymongo_error, DuplicateKeyError):
                                response["status_code"] = 409
                            elif isinstance(pymongo_error, ObjectNotFoundError):
                                response["status_code"] = 404
                            else:
                                response["status_code"] = 400
                        except KubernetesException as kube_error:
                            response.update(dict(
                                status_code=kube_error.status_code, body=dict(message=kube_error.message)
                            ))

            else:
                error = "Action %s does not support operations." % request["action"]
                response.update(dict(status_code=400, body=dict(message=error)))

            yield self.write_message(response)

        elif request["operation"] in WATCH_OPERATIONS:
            watcher_key = self._get_watcher_key(request)

            if request["operation"] == "watch":
                response["operation"] = "watched"

                watcher_cls = self.actions_lookup[request["action"]].get("watcher_cls", None)
                if watcher_cls:
                    if watcher_key in self.current_watchers.keys():
                        response["body"] = {"message": "Action already watched."}
                        response["status_code"] = 400
                        yield self.write_message(response)

                    else:
                        watcher = watcher_cls(request, self.settings, self.user, self.write_message)
                        if not (yield watcher.check_permissions(request["operation"], body)):
                            error = "Operation %s forbidden for action %s." % (request["operation"], request["action"])
                            response.update(dict(status_code=403, body=dict(message=error)))
                        else:
                            yield watcher.watch()
                            self.current_watchers[watcher_key] = watcher
                else:
                    response["body"] = {"message": "Action not supported for operation watch."}
                    response["status_code"] = 400
                    yield self.write_message(response)

            elif request["operation"] == "unwatch":
                response["operation"] = "unwatched"
                if watcher_key in self.current_watchers.keys():
                    self.current_watchers[watcher_key].unwatch()
                    del self.current_watchers[watcher_key]
                else:
                    response["body"] = {"message": "Action not previously watch."}
                    response["status_code"] = 400

                yield self.write_message(response)

    @coroutine
    def on_close(self):
        logging.info("Closing MainWebSocketHandler")

        for key, watcher in self.current_watchers.iteritems():
            logging.debug("Closing watcher %s", key)
            watcher.unwatch()

        yield super(MainWebSocketHandler, self).on_close()

    @coroutine
    def validate_message(self, message):
        try:
            request = loads(message)
        except ValueError:
            self.write_message("Message '%s' cannot be deserialized" % message)
            raise Return(None)

        if "action" not in request:
            self.write_message("Message %s does not contain 'action'" % message)
            raise Return(None)

        if "operation" not in request:
            self.write_message("Message %s does not contain 'operation'" % message)
            raise Return(None)

        if "correlation" not in request:
            self.write_message("Message %s does not contain 'correlation'" % message)
            raise Return(None)

        if request["action"] not in SUPPORTED_ACTIONS:
            self.write_message(dict(
                action=request["action"],
                operation=request["operation"],
                correlation=request["correlation"],
                body={"message": "Action %s not supported." % request["action"]},
                status_code=400
            ))

            raise Return(None)

        if request["operation"] not in REST_OPERATIONS + WATCH_OPERATIONS:
            self.write_message(dict(
                action=request["action"],
                operation=request["operation"],
                correlation=request["correlation"],
                body={"message": "Operation %s not supported." % request["operation"]},
                status_code=400
            ))

            raise Return(None)

        raise Return(request)

    def build_actions_lookup(self):
        self.actions_lookup = dict(
            charts=dict(
                watcher_cls=CursorWatcher
            ),
            logs=dict(
                rest=LogsActions(self.settings, self.user)
            ),
            instance=dict(
                watcher_cls=KubeWatcher
            ),
            instances=dict(
                rest=InstancesActions(self.settings, self.user),
                watcher_cls=KubeWatcher
            ),
            metrics=dict(
                watcher_cls=MetricsWatcher
            ),
            namespaces=dict(
                rest=NamespacesActions(self.settings, self.user),
                watcher_cls=CursorWatcher
            ),
            settings=dict(
                rest=SettingsActions(self.settings, self.user),
                watcher_cls=CursorWatcher
            ),
            users=dict(
                rest=UsersActions(self.settings, self.user),
                watcher_cls=CursorWatcher
            ),
            invitations=dict(
                rest=InvitationsActions(self.settings, self.user),
            ),
            notifications=dict(
                rest=NotificationsActions(self.settings, self.user),
                watcher_cls=CursorWatcher
            ),
        )

    @staticmethod
    def _get_watcher_key(message):
        watcher_key = message["action"]

        if "body" in message:
            if "namespace" in message["body"]:
                watcher_key += ".%s" % message["body"]["namespace"]

            if "kind" in message["body"]:
                watcher_key += ".%s" % message["body"]["kind"]

            if "name" in message["body"]:
                watcher_key += ".%s" % message["body"]["name"]

        return watcher_key
