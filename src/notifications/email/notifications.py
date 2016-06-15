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
import time

from datetime import datetime, date, timedelta
# from smtplib import SMTP, SMTP_SSL
from tornado.gen import coroutine, Return, sleep

from data.query import Query
from data.watch import add_callback


class EmailNotifications(object):

    def __init__(self, database):
        logging.info("Initializing EmailNotifications.")

        self.database = database
        self.mail_settings = None

    @coroutine
    def update_smtp(self, document):
        logging.info("Settings updated")
        self.mail_settings = document['o']["mail"] if "mail" in document['o'] else None

    @coroutine
    def sync_loop(self):
        logging.info("Initializing sync loop.")

        yield add_callback("Settings", self.update_smtp)

        settings = yield Query(self.database, "Settings").find_one() or dict()
        if "mail" in settings:
            logging.warn(settings["mail"])
            self.mail_settings = settings["mail"]
            # self.server = smtp_config['server']
            # self.port = int(smtp_config['port'])
            # self.sender = smtp_config['no_reply_address']
            # self.secure = smtp_config.get('ssl', True)

        while True:
            try:
                if self.mail_settings:
                    logging.info("Checking for pending notifications to send")
                    users = yield self.get_pending_users()
                    for user in users:
                        notifications = yield self.get_notifications(user)
                        yesterday = datetime.utcnow() - timedelta(days=1)

                        logging.info("User %s has %s pending notifications of %s",
                            user["username"], len(notifications), yesterday)

                        # TODO: Generate body and Send email
                        body = self.generate_notifications_template(user, notifications, yesterday)

                else:
                    logging.warn("Outbound email is turned off")

            except:
                logging.exception("Failed sending email notifications.")

            yield sleep(5)

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
    def get_notifications(self, user):
        today = datetime.utcnow()
        today = datetime(today.year, today.month, today.day)
        to_time = time.mktime(today.timetuple()) + today.microsecond / 1E6
        from_time = to_time - 86400

        namespaces_criteria = yield self.get_namespaces_criteria(user)

        notifications = yield Query(self.database, "Notifications").find({'$and': [
            namespaces_criteria,
            {'metadata.creationTimestamp': {'$gte': from_time}},
            {'metadata.creationTimestamp': {'$lt': to_time}}
        ]})

        raise Return(notifications)

    @coroutine
    def get_namespaces_criteria(self, user):
        criteria = {}

        if user["role"] != "administrator":
            namespaces = yield Query(self.database, "Namespaces").find(
                criteria={"members": user["username"]},
                projection=["name"])
            criteria["namespace"] = {'$in': [n["name"] for n in namespaces]}

        raise Return(criteria)

    def generate_notifications_template(self, user, notifications, notifications_date):

        return "EMAIL CONTENT"

    # def start_connection(secure, server, port):
    #     connection = None
    #     if secure:
    #         try:
    #             connection = SMTP_SSL(server, port)
    #         except Exception:
    #             connection = None  # SSL/TLS is not available, fallback to starttls
    #             logging.info('Fall back to STARTTLS connection')

    #         if connection is None:
    #             connection = SMTP(server, port)
    #             connection.set_debuglevel(True)
    #             connection.starttls()

    #     else:
    #         connection = SMTP(server, port)

    #     return connection

    # def send(smtp_config, address, subject, body, body_type):
    #     server = smtp_config['server']
    #     port = int(smtp_config['port'])
    #     sender = smtp_config['no_reply_address']
    #     logging.debug('Sending mail "%s" from "%s" to "%s" with server "%s"', subject, sender, address, server)

    #     try:
    #         connection = start_connection(smtp_config.get('ssl', True), server, port)
    #         connection.set_debuglevel(False)
    #     except Exception:
    #         logging.exception('Fail back to start SMTP connection')
    #         raise

    #     authentication = smtp_config.get('authentication')
    #     if authentication is not None:
    #         connection.login(authentication['username'].encode('utf-8'), authentication['password'].encode('utf-8'))

    #     sender = smtp_config['no_reply_address']

    #     message = MIMEText(body, body_type)
    #     message['Subject'] = subject
    #     message['From'] = sender
    #     try:
    #         connection.sendmail(sender, address, message.as_string())
    #     finally:
    #         connection.close()

    #     logging.debug("Mail sent")
