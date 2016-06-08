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
import os

from motor.motor_tornado import MotorClient
from tornado.gen import coroutine
from tornado.ioloop import IOLoop

from notifications.daily.notifications import EmailNotifications
from data import watch


@coroutine
def initialize():
    logging.info("Initializing email notifications")

    mongo_url = "mongodb://{0}:{1}/".format(
        os.getenv("ELASTICKUBE_MONGO_SERVICE_HOST", "localhost"),
        os.getenv("ELASTICKUBE_MONGO_SERVICE_PORT", 27017)
    )

    motor_client = MotorClient(mongo_url)

    try:
        watch.start_monitor(motor_client)
        yield EmailNotifications(motor_client.elastickube).sync_loop()
    except:
        logging.exception("Unexpected error executing EmailNotifications sync loop.")
        IOLoop.current().stop()
