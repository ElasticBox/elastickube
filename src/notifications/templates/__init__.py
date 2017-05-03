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
import os

from datetime import datetime
from tornado.gen import coroutine, Return

from data.query import Query

TEMPLATE_PATH = os.path.dirname(os.path.abspath(__file__))

NOTIFICATIONS_SUBJECT = u"[ElasticKube] Notifications for {} - {} updates in {} namespaces"

with open(os.path.join(TEMPLATE_PATH, 'notifications.html')) as invite_file:
    NOTIFICATIONS_TEMPLATE = invite_file.read()

with open(os.path.join(TEMPLATE_PATH, 'namespace_details.html')) as invite_file:
    NAMESPACE_TEMPLATE = invite_file.read()

with open(os.path.join(TEMPLATE_PATH, 'notification_detail.html')) as invite_file:
    NOTIFICATION_TEMPLATE = invite_file.read()


class NotificationTemplate(object):

    def __init__(self, database, hostname):
        logging.info("Initializing NotificationTemplate.")

        self.database = database
        self.hostname = hostname

    @coroutine
    def generate_template(self, user, notifications, notifications_date):
        ns_details = {}
        for notification in notifications:
            if 'namespace' in notification:
                desc = yield self._notification_description(notification, user)
                if notification["namespace"] not in ns_details:
                    ns_details[notification["namespace"]] = desc
                else:
                    ns_details[notification["namespace"]] += desc

        details = ""
        for key, value in ns_details.iteritems():
            details += NAMESPACE_TEMPLATE.format(
                namespace=key,
                notifications=value,
                namespace_link="{0}/{1}/instances".format(self.hostname, key))

        body = NOTIFICATIONS_TEMPLATE.format(
            date=notifications_date.strftime("%A, %B %d, %Y"),
            notifications=details,
            notification_settings_link=self.hostname)

        subject = NOTIFICATIONS_SUBJECT.format(
            notifications_date.strftime("%b %d, %Y"), len(notifications), len(ns_details.keys()))

        raise Return((body, subject))

    @coroutine
    def _notification_description(self, notification, user):
        user_description = yield self._get_user_description(notification["user"])
        action = yield self._get_action_text(notification, user)
        target_resource = yield self._get_target_resource_name(notification)
        notification_time = datetime.utcfromtimestamp(
            notification["metadata"]["creationTimestamp"]).strftime("[%I:%M%p]")

        raise Return(NOTIFICATION_TEMPLATE.format(
            description="{0} {1} {2}".format(user_description, action, target_resource),
            notification_link="{0}/notifications".format(self.hostname),
            time=notification_time)
        )

    @coroutine
    def _get_action_text(self, notification, user):
        resource = notification["resource"]

        if notification["operation"] == 'create':
            action = 'created' if notification["action"] != 'User' else 'invited to'

        elif notification["operation"] == 'delete':
            if resource["kind"] in ('Pod', 'ReplicationController', 'Service'):
                action = 'deleted {0}'.format(resource["kind"])
            else:
                action = 'deleted'

        elif notification["operation"] == 'add':
            if resource["kind"] == 'User':
                name = yield self._get_user_description(resource["name"], user)
                action = 'added {0} to'.format(name)
            else:
                action = 'added'

        elif notification["operation"] == 'remove':
            if resource["kind"] == 'User':
                name = yield self._get_user_description(resource["name"], user)
                action = 'removed {0} from'.format(name)
            else:
                action = 'removed'

        elif notification["operation"] == 'deploy':
            action = 'deployed'

        else:
            action = notification["operation"]

        raise Return(action)

    @coroutine
    def _get_user_description(self, username, current_user=None):
        if current_user is not None and current_user["username"] == username:
            raise Return('you')

        user = yield Query(self.database, "Users").find_one({"username": username})
        if user is not None and (user["firstname"] or user["lastname"]):
            raise Return('{0} {1}'.format(user["firstname"], user["lastname"]))

        raise Return(username)

    @coroutine
    def _get_target_resource_name(self, notification):
        resource = notification["resource"]

        if resource["kind"] == 'User':
            if notification["operation"] == 'create':
                name = yield self._get_user_description(resource["name"])
                raise Return(name)

            raise Return(notification["namespace"])

        elif resource["kind"] in ('Pod', 'ReplicationController', 'Service'):
            raise Return("{0}/{1}".format(notification["namespace"], resource["name"]))

        elif resource["kind"] == 'Chart':
            if "namespace" in notification:
                raise Return("{0}/{1}".format(notification["namespace"], resource["name"]))
            raise Return(resource["name"])

        raise Return(resource["name"])
