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

from bson.objectid import ObjectId
from tornado.gen import coroutine, Return

from api.kube.exceptions import KubernetesException
from api.v1.auth import Saml2LoginHandler
from data.query import Query, ObjectNotFoundError


class SettingsActions(object):

    def __init__(self, settings, user):
        logging.info("Initializing SettingsActions")

        self.database = settings["database"]
        self.user = user
        self.notifications = []

    @coroutine
    def check_permissions(self, operation, _request_body):
        logging.debug("check_permissions for user %s and operation %s on settings", self.user["username"], operation)
        raise Return(self.user["role"] == "administrator")

    @coroutine
    def update(self, document):
        logging.info("Updating Setting document with _id: %s", document["_id"])

        initial_settings = yield Query(self.database, "Settings").find_one({"_id": ObjectId(document["_id"])})
        if not initial_settings:
            raise ObjectNotFoundError("User %s not found." % document["_id"])

        saml_config = document[u'authentication'].get("saml", None)
        if saml_config is not None:
            try:
                idp_entity_id, idp_domain, idp_cert, idp_sso = Saml2LoginHandler.get_metadata_info(
                    saml_config.get("metadata", None))
            except Exception:
                logging.exception("Error parsing metadata")
                raise KubernetesException(
                    "Invalid SAML IdP metadata file {0}".format(saml_config.get("metadata_file", "")), 400)

            saml_config["idp_entity_id"] = idp_entity_id
            saml_config["idp_domain"] = idp_domain
            saml_config["idp_cert"] = idp_cert
            saml_config["idp_sso"] = idp_sso

        updated_settings = yield Query(self.database, "Settings").update(document)
        raise Return((initial_settings, updated_settings))
