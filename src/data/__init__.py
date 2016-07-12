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

from tornado.gen import coroutine

DEFAULT_GITREPO = "https://github.com/helm/charts.git"
DEFAULT_PASSWORD_REGEX = "^.{8,256}$"
SCHEMA_VERSION = 4


@coroutine
def init(database):
    logging.info("Initializing database...")

    yield setup_indexes(database)

    settings = yield database.Settings.find_one({"metadata.deletionTimestamp": None})

    if not settings:
        result = yield database.Settings.insert({
            "schema": "http://elasticbox.net/schemas/settings",
            "metadata": {
                "resourceVersion": time.time(),
                "creationTimestamp": time.time(),
                "deletionTimestamp": None
            },
            "charts": {
                "repo_url": DEFAULT_GITREPO
            },
            "authentication": {
                "password": {
                    "regex": DEFAULT_PASSWORD_REGEX
                }
            },
            "schema_version": SCHEMA_VERSION
        })

        logging.debug("Initial Settings document created, %s", result)
    else:
        if settings["schema_version"] != SCHEMA_VERSION:
            yield migrate(database, settings)


@coroutine
def setup_indexes(database):
    yield database.Users.ensure_index(key_or_list="email", unique=True, sparse=True)
    yield database.Users.ensure_index(key_or_list="username", unique=True, sparse=True)
    yield database.Users.ensure_index(key_or_list="metadata.deletionTimestamp", unique=False, sparse=True)


@coroutine
def migrate(database, settings):
    logging.debug("Migrating DB from version %d to %d", settings["schema_version"], SCHEMA_VERSION)

    if settings["schema_version"] == 1:
        settings["charts"] = {
            "repo_url": DEFAULT_GITREPO
        }
        settings["schema_version"] = 2

    if settings["schema_version"] == 2:

        cursor = database.Users.find()

        while (yield cursor.fetch_next):
            user = cursor.next_object()
            if "password" in user:
                user["password"] = dict(
                    salt=user["password"]["salt"],
                    rounds='$6$rounds=40000$',
                    hash=user["password"]["hash"].split("$rounds=40000$")[1]
                )
                database.Users.update({"_id": user["_id"]}, user)

        settings["schema_version"] = 3
        database.Settings.update({"_id": settings["_id"]}, settings)

    if settings["schema_version"] == 3:
        admins = []
        admins_cursor = database.Users.find({'role': 'administrator'})
        while (yield admins_cursor.fetch_next):
            admins.append(admins_cursor.next_object()["username"])

        namespaces_cursor = database.Namespaces.find()
        while (yield namespaces_cursor.fetch_next):
            namespace = namespaces_cursor.next_object()
            if "members" in namespace:
                namespace["members"] = list(set(admins + namespace["members"]))
            else:
                namespace["members"] = admins

            yield database.Namespaces.update({"_id": namespace["_id"]}, namespace)

        yield database.Users.update({"notifications": {"$exists": False}},
                                    {"$set": {"notifications": {"namespace": True}}},
                                    multi=True)

        settings["schema_version"] = 4
        database.Settings.update({"_id": settings["_id"]}, settings)
