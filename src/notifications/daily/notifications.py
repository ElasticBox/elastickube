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

from __future__ import absolute_import

import logging
import time
from datetime import datetime, timedelta
from smtplib import SMTP, SMTP_SSL

from bson.objectid import ObjectId
from email.MIMEText import MIMEText
from tornado.gen import coroutine, Return, sleep

from data.query import Query, ObjectNotFoundError
from data.watch import add_callback
from notifications.templates import NotificationTemplate

HTML_BODY_TYPE = 'html'


class EmailNotifications(object):

    def __init__(self, database):
        logging.info("Initializing EmailNotifications.")

        self.database = database
        self.mail_settings = None
        self.notification_template = None

    @coroutine
    def update_smtp(self, document):
        logging.info("Settings updated")
        self.mail_settings = document['o']["mail"] if "mail" in document['o'] else None
        self.notification_template = NotificationTemplate(self.database, document['o']["hostname"])

    @coroutine
    def sync_loop(self):
        logging.info("Initializing sync loop.")

        yield add_callback("Settings", self.update_smtp)

        settings = yield Query(self.database, "Settings").find_one() or dict()
        if "mail" in settings:
            self.mail_settings = settings["mail"]
            self.notification_template = NotificationTemplate(self.database, settings["hostname"])

        while True:
            try:
                if self.mail_settings:
                    logging.info("Checking for pending notifications to send")

                    users = yield self.get_pending_users()
                    for user in users:
                        notifications = yield self.get_notifications(user)
                        yesterday = datetime.utcnow() - timedelta(days=1)

                        logging.info(
                            "User %s has %s pending notifications for %s",
                            user["username"],
                            len(notifications),
                            yesterday.strftime("%b %d, %Y")
                        )

                        body, subject = yield self.notification_template.generate_template(
                            user, notifications, yesterday)

                        self.send(self.mail_settings, user["username"], subject, body, HTML_BODY_TYPE)
                        yield self.update_user_notified(user)
                else:
                    logging.info("Outbound email is turned off")
            except Exception:
                logging.exception("Failed sending email notifications.")

            yield sleep(600)

    @coroutine
    def get_pending_users(self):
        today = datetime.utcnow()
        today = datetime(today.year, today.month, today.day)

        users = yield Query(self.database, "Users").find({'$and': [
            {'notifications.namespace': True},
            {'$or': [
                {'notifications.notified_at': {'$exists': False}},
                {'notifications.notified_at': {'$lt': today - timedelta(days=1)}}
            ]}
        ]})

        raise Return(users)

    @coroutine
    def update_user_notified(self, user):
        notified_at = datetime.utcnow()
        logging.debug("Updating user %s to notified at %s", user["username"], notified_at)

        user = yield Query(self.database, "Users").find_one({"_id": ObjectId(user['_id'])})
        if not user:
            raise ObjectNotFoundError("User %s not found." % user["_id"])

        if "notifications" in user:
            user["notifications"]["notified_at"] = notified_at
            yield Query(self.database, "Users").update(user)

        raise Return(True)

    @coroutine
    def get_notifications(self, user):
        today = datetime.utcnow()
        today = datetime(today.year, today.month, today.day)
        to_time = time.mktime(today.timetuple()) + today.microsecond / 1E6
        from_time = to_time - 86400

        notifications = yield Query(self.database, "Notifications").find({'$and': [
            {'user': user['username']},
            {'unread': True},
            {'metadata.creationTimestamp': {'$gte': from_time}},
            {'metadata.creationTimestamp': {'$lt': to_time}}
        ]})

        raise Return(notifications)

    def start_connection(self, secure, server, port):
        connection = None
        if secure:
            try:
                connection = SMTP_SSL(server, port)
            except Exception:
                connection = None  # SSL/TLS is not available, fallback to starttls
                logging.warn('Fall back to STARTTLS connection')

            if connection is None:
                connection = SMTP(server, port)
                connection.set_debuglevel(True)
                connection.starttls()

        else:
            connection = SMTP(server, port)

        return connection

    def send(self, smtp_config, address, subject, body, body_type):
        server = smtp_config['server']
        port = int(smtp_config['port'])
        sender = smtp_config['no_reply_address']
        logging.debug('Sending mail "%s" from "%s" to "%s" with server "%s"', subject, sender, address, server)

        try:
            connection = self.start_connection(smtp_config.get('ssl', True), server, port)
            connection.set_debuglevel(False)
        except Exception:
            logging.exception('Fail back to start SMTP connection')
            raise

        authentication = smtp_config.get('authentication')
        if authentication is not None:
            connection.login(authentication['username'].encode('utf-8'), authentication['password'].encode('utf-8'))

        sender = smtp_config['no_reply_address']

        message = MIMEText(body, body_type)
        message['Subject'] = subject
        message['From'] = sender
        try:
            connection.sendmail(sender, address, message.as_string())
        finally:
            connection.close()

        logging.debug("Mail sent")
