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

import cgi
import json
import logging
import random
import re
import string
import urlparse
from datetime import datetime, timedelta

import jwt
from bson.objectid import ObjectId
from lxml import etree
from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from onelogin.saml2.metadata import OneLogin_Saml2_Metadata
from passlib.hash import sha512_crypt
from tornado.auth import GoogleOAuth2Mixin
from tornado.gen import coroutine, Return
from tornado.web import RequestHandler, HTTPError

from api.v1 import ELASTICKUBE_TOKEN_HEADER, ELASTICKUBE_VALIDATION_TOKEN_HEADER
from api.v1.actions import emails
from data.query import Query


ROUNDS = 40000


def _generate_hashed_password(password):
    salt = "".join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(64))
    generated_hash = sha512_crypt.encrypt((password + salt).encode("utf-8"), rounds=ROUNDS)
    hash_parts = generated_hash.split("$rounds={0}$".format(ROUNDS))
    return {"hash": hash_parts[1], "rounds": "{0}$rounds={1}$".format(hash_parts[0], ROUNDS), "salt": salt}


def _fill_signup_invitation_request(document, firstname, lastname, password=None):
    document["firstname"] = firstname
    document["lastname"] = lastname
    document["email_validated_at"] = datetime.utcnow()
    if password is not None:
        document["password"] = _generate_hashed_password(password)


class AuthHandler(RequestHandler):

    @coroutine
    def authenticate_user(self, user):
        logging.info("Authenticating user '%(username)s'", user)

        token = dict(
            id=str(user["_id"]),
            username=user["username"],
            firstname=user["firstname"],
            lastname=user["lastname"],
            email=user["email"],
            role=user["role"],
            created=datetime.utcnow().isoformat(),
            exp=datetime.utcnow() + timedelta(30)
        )

        user["last_login"] = datetime.utcnow()
        yield self.settings["database"].Users.update({"_id": user["_id"]}, user)

        token = jwt.encode(token, self.settings["secret"], algorithm="HS256")
        self.set_cookie(ELASTICKUBE_TOKEN_HEADER, token)

        logging.info("User '%(username)s' authenticated.", user)
        raise Return(token)


class AuthProvidersHandler(RequestHandler):

    @coroutine
    def get(self):
        providers = dict()

        # If there are no users created then we need to return an empty list of providers to enable the signup flow
        if (yield Query(self.settings["database"], "Users").find_one()) is None:
            self.write({})
        else:
            settings = yield Query(self.settings["database"], "Settings").find_one()

            if "google_oauth" in settings["authentication"]:
                providers['google'] = dict(auth_url="/api/v1/auth/google")

            if "saml" in settings["authentication"]:
                providers['saml'] = dict(auth_url="/api/v1/auth/saml")

            if "password" in settings["authentication"]:
                providers['password'] = dict(regex=settings["authentication"]["password"]["regex"])

            validation_token = self.request.headers.get(ELASTICKUBE_VALIDATION_TOKEN_HEADER)
            if validation_token is not None:
                user = yield Query(self.settings["database"], "Users").find_one({"invite_token": validation_token})
                if user is not None and 'email_validated_at' not in user:
                    providers['email'] = user[u'email']

            self.write(providers)


class SignupHandler(AuthHandler):

    @staticmethod
    def _validate_signup_data(data):
        if "email" not in data:
            raise HTTPError(400, reason="Email is required.")

        if "password" not in data:
            raise HTTPError(400, reason="Password is required.")

        if "firstname" not in data:
            raise HTTPError(400, reason="First name is required.")

        if "lastname" not in data:
            raise HTTPError(400, reason="Last name is required.")

        return True

    @coroutine
    def _update_invited_user(self, validation_token, data):
        user = yield Query(self.settings["database"], "Users").find_one(
            {"invite_token": validation_token, "email": data["email"]})

        if user is not None and "email_validated_at" not in user:
            for namespace_name in user["namespaces"]:
                namespace = yield Query(self.settings["database"], "Namespaces").find_one({"name": namespace_name})
                if namespace is None:
                    logging.warn("Cannot find namespace %s", namespace_name)
                else:
                    if "members" in namespace:
                        namespace["members"].append(user["username"])
                    else:
                        namespace["members"] = [user["username"]]

                    yield Query(self.settings["database"], "Namespaces").update(namespace)

            del user["namespaces"]

            _fill_signup_invitation_request(
                user, firstname=data["firstname"], lastname=data["lastname"],
                password=data["password"])

            raise Return(user)
        else:
            raise HTTPError(403, message="Invitation not found.")

    @coroutine
    def post(self):
        try:
            data = json.loads(self.request.body)
        except Exception:
            raise HTTPError(400, message='Invalid JSON')

        validation_token = self.request.headers.get(ELASTICKUBE_VALIDATION_TOKEN_HEADER)
        if validation_token is not None:
            self._validate_signup_data(data)
            user = yield self._update_invited_user(validation_token, data)
            token = yield self.authenticate_user(user)
            self.write(token)
            self.flush()

        # Signup can be used only the first time
        elif (yield Query(self.settings["database"], "Users").find_one()) is not None:
            raise HTTPError(403, message="Onboarding already completed.")

        else:
            self._validate_signup_data(data)

            user = dict(
                email=data["email"],
                username=data["email"],
                password=_generate_hashed_password(data["password"]),
                firstname=data["firstname"],
                lastname=data["lastname"],
                role="administrator",
                schema="http://elasticbox.net/schemas/user",
                email_validated_at=datetime.utcnow().isoformat()
            )

            signup_user = yield Query(self.settings["database"], "Users").insert(user)
            namespaces = yield Query(self.settings["database"], "Namespaces").find()
            for namespace in namespaces:
                if "members" in namespace:
                    namespace["members"].append(signup_user["username"])
                else:
                    namespace["members"] = [signup_user["username"]]

                yield Query(self.settings["database"], "Namespaces").update(namespace)

            token = yield self.authenticate_user(signup_user)
            self.write(token)
            self.flush()


class RequestInviteHandler(AuthHandler):

    @coroutine
    def post(self):
        logging.info("Initiating RequestInviteHandler post")
        data = json.loads(self.request.body)
        if "email" not in data:
            raise HTTPError(400, reason="Missing email in body request.")

        settings = yield self.settings["database"].Settings.find_one()
        if "mail" in settings:
            mail_settings = settings["mail"]

            origin_user = {
                'name': data.get('name', ''),
                'email': data['email']
            }

            invite_address = "{0}/admin/users?invite={1}".format(
                settings["hostname"], cgi.escape(origin_user['email'], quote=True))
            try:
                admin = yield Query(self.settings["database"], "Users").find_one({"role": "administrator"})
                yield emails.send_request_invite_link(
                    mail_settings, admin["email"], origin_user, invite_address, settings)

            except Exception:
                logging.exception("Error sending request invite.")
                raise HTTPError(500, reason='Error sending request invite.')
            raise HTTPError(200)
        else:
            logging.warning("Mail settings not added")
            raise HTTPError(412, reason="Request invite not available.")


class ResetPasswordHandler(AuthHandler):

    @coroutine
    def post(self):
        logging.info("Initiating ResetPasswordHandler post")

        data = json.loads(self.request.body)
        if "email" not in data:
            raise HTTPError(400, reason="Missing email in body request.")

        email = data["email"]

        user = yield self.settings["database"].Users.find_one({"email": email})

        if not user:
            logging.debug("User with email '%s' not found.", email)
            raise HTTPError(200)

        settings = yield self.settings["database"].Settings.find_one()
        if "mail" in settings:
            mail_settings = settings["mail"]

            token = dict(
                id=str(user["_id"]),
                hash=user['password']['hash'][:-16],
                exp=datetime.utcnow() + timedelta(minutes=10)
            )

            token = jwt.encode(token, self.settings["secret"], algorithm="HS256")

            user_data = {
                'name': user.get('firstname'),
                'email': user['email'],
                'token': token
            }

            try:
                yield emails.send_reset_password_link(mail_settings, user_data, settings)
            except Exception:
                raise HTTPError(500, reason='Error sending reset password email.')
            raise HTTPError(200)
        else:
            logging.warning("Mail settings not added")
            raise HTTPError(412, reason="Mail settings not added.")


class ChangePasswordHandler(AuthHandler):

    @coroutine
    def post(self):
        logging.info("Initiating ChangePasswordHandler post")

        data = json.loads(self.request.body)
        if "password" not in data:
            raise HTTPError(400, reason="Missing arguments in change password request.")

        if "token" not in data:
            raise HTTPError(400, reason="Missing arguments in change password request.")

        password = data["password"]

        try:
            token = jwt.decode(data["token"], self.settings['secret'], algorithm='HS256')
        except Exception:
            raise HTTPError(400, reason="Invalid token or token has expired")

        user = yield self.settings["database"].Users.find_one({"_id": ObjectId(token["id"])})

        if not user:
            logging.error("Error trying to change user password for token: '%s'.", token)
            raise HTTPError(200)

        if not user["password"]["hash"][:-16] == token["hash"]:
            raise HTTPError(400, reason="Invalid token or token has expired")

        user["password"] = _generate_hashed_password(password)

        yield Query(self.settings["database"], "Users").update_fields({"_id": user["_id"]}, {
            "password": user["password"]
        })
        raise HTTPError(200)


class PasswordHandler(AuthHandler):

    @coroutine
    def post(self):
        logging.info("Initiating PasswordHandler post")

        data = json.loads(self.request.body)
        if "username" not in data:
            raise HTTPError(400, reason="Missing username in body request.")

        if "password" not in data:
            raise HTTPError(400, reason="Missing password in body request.")

        username = data["username"]
        password = data["password"]

        user = yield self.settings["database"].Users.find_one({"username": username})
        if not user:
            logging.info("Username '%s' not found.", username)
            raise HTTPError(302, reason='/request-invite')

        if 'email_validated_at' not in user:
            logging.info("Username '%s' not validated.", username)
            raise HTTPError(302, reason='/request-invite')

        if 'password' not in user:
            logging.info("User '%s' has not password.", username)
            raise HTTPError(401, reason="Invalid username or password.")

        encoded_user_password = '{0}{1}'.format(user["password"]["rounds"], user["password"]["hash"])
        if sha512_crypt.verify((password + user["password"]["salt"]).encode("utf-8"), encoded_user_password):
            token = yield self.authenticate_user(user)
            self.write(token)
            self.flush()
        else:
            logging.info("Invalid password for user '%s'.", username)
            raise HTTPError(401, reason="Invalid username or password.")


class GoogleOAuth2LoginHandler(AuthHandler, GoogleOAuth2Mixin):

    @coroutine
    def get(self):
        logging.info("Initiating Google OAuth.")

        settings = yield Query(self.settings["database"], "Settings").find_one()
        google_oauth = settings[u'authentication'].get('google_oauth', None)
        if google_oauth is None:
            raise HTTPError(403, 'Forbidden request')

        # Add OAuth settings for GoogleOAuth2Mixin
        self.settings['google_oauth'] = {
            'key': google_oauth['key'],
            'secret': google_oauth['secret']
        }

        code = self.get_argument('code', False)
        redirect_uri = "{0}/api/v1/auth/google".format(settings["hostname"])
        if code:
            logging.debug("Google redirect received.")

            auth_data = yield self.get_authenticated_user(
                redirect_uri=redirect_uri,
                code=code)

            auth_user = yield self.oauth2_request(
                "https://www.googleapis.com/oauth2/v1/userinfo",
                access_token=auth_data['access_token'])

            if auth_user["verified_email"]:
                user = yield self.settings["database"].Users.find_one({"email": auth_user["email"]})
                firstname = auth_data.get('given_name', auth_data.get('name', ""))
                lastname = auth_data.get('family_name', "")

                # Validate user if it signup by OAuth2
                if user and 'email_validated_at' not in user:
                    logging.debug('User validated via OAuth2 %s', auth_user["email"])
                    _fill_signup_invitation_request(user, firstname=firstname, lastname=lastname, password=None)
                    user = yield Query(self.settings["database"], 'Users').update(user)

                if user:
                    yield self.authenticate_user(user)
                    self.redirect('/')
                else:
                    logging.debug("User '%s' not found", auth_user["email"])
                    self.redirect('/request-invite?account={0}&name={1}'.format(
                        cgi.escape(auth_user["email"], quote=True),
                        cgi.escape("{0} {1}".format(firstname, lastname), quote=True)))

            else:
                logging.info("User email '%s' not verified.", auth_user["email"])
                raise HTTPError(400, "Email is not verified.")
        else:
            logging.debug("Redirecting to google for authentication.")
            yield self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=google_oauth['key'],
                scope=['profile', 'email'],
                response_type='code',
                extra_params={'approval_prompt': 'auto'})


class Saml2MetadataHandler(RequestHandler):

    @coroutine
    def get(self):
        logging.info("Initiating SAML 2.0 Metadata get.")

        settings = yield Query(self.settings["database"], "Settings").find_one()
        saml_settings = Saml2MetadataHandler.get_saml_settings(settings)

        self.set_header('Content-Type', 'text/xml')
        self.write(OneLogin_Saml2_Metadata.builder(
            sp=saml_settings['sp'],
            authnsign=saml_settings['security']['authnRequestsSigned'],
            wsign=saml_settings['security']['wantAssertionsSigned'])
        )
        self.flush()

    @staticmethod
    def get_saml_settings(settings, saml_config=None):
        saml_settings = dict(
            sp=dict(
                entityId=urlparse.urlparse(settings["hostname"]).netloc,
                assertionConsumerService=dict(
                    url="{0}/api/v1/auth/saml".format(settings["hostname"]),
                    binding=OneLogin_Saml2_Constants.BINDING_HTTP_POST),
                NameIDFormat=OneLogin_Saml2_Constants.NAMEID_UNSPECIFIED,
                attributeConsumingService=dict(
                    serviceName="ElasticKube SAML",
                    serviceDescription="ElasticKube SAML Service Provider",
                    requestedAttributes=[]
                )
            ),
            security=dict(
                authnRequestsSigned=False,
                wantAssertionsSigned=True,
                wantNameId=True
            )
        )

        if saml_config is not None:
            saml_settings['idp'] = dict(
                entityId=saml_config['idp_entity_id'],
                singleSignOnService=dict(
                    url=saml_config['idp_sso'],
                    binding=OneLogin_Saml2_Constants.BINDING_HTTP_REDIRECT),
                x509cert=saml_config['idp_cert']
            )

        return saml_settings


class Saml2LoginHandler(AuthHandler):

    NS_IDENTITY_CLAIMS = 'http://schemas.xmlsoap.org/ws/2005/05/identity/claims/'
    EMAIL_ATTRIBUTES = ('email', 'Email', 'User.Email', NS_IDENTITY_CLAIMS + 'email')
    FIRST_NAME_ATTRIBUTES = ('firstname', 'FirstName', 'User.FirstName', NS_IDENTITY_CLAIMS + 'givenname')
    LAST_NAME_ATTRIBUTES = ('lastname', 'LastName', 'User.LastName', NS_IDENTITY_CLAIMS + 'surname')

    IDP_CERT_PATH = "md:IDPSSODescriptor/md:KeyDescriptor[@use='signing']/ds:KeyInfo/ds:X509Data/ds:X509Certificate"
    IDP_SSO_PATH = "md:IDPSSODescriptor/md:SingleSignOnService[@Binding='{0}']".format(
        OneLogin_Saml2_Constants.BINDING_HTTP_REDIRECT)

    @staticmethod
    def get_metadata_info(metadata):
        metadata_xml = etree.fromstring(str(metadata))

        if metadata_xml.tag.endswith('EntitiesDescriptor'):
            metadata_xml = metadata_xml.find("md:EntityDescriptor", namespaces=OneLogin_Saml2_Constants.NSMAP)

        idp_entity_id = metadata_xml.attrib['entityID']
        idp_domain = urlparse.urlparse(idp_entity_id).netloc
        idp_cert = metadata_xml.find(Saml2LoginHandler.IDP_CERT_PATH, namespaces=OneLogin_Saml2_Constants.NSMAP).text
        idp_sso = metadata_xml.find(
            Saml2LoginHandler.IDP_SSO_PATH, namespaces=OneLogin_Saml2_Constants.NSMAP).attrib['Location']

        return idp_entity_id, idp_domain, idp_cert, idp_sso

    @coroutine
    def _get_saml_auth(self, request):
        settings = yield Query(self.settings["database"], "Settings").find_one()
        saml_config = settings[u'authentication'].get('saml', None)
        if saml_config is None:
            raise HTTPError(403, 'Forbidden request')

        netloc = urlparse.urlparse(settings["hostname"]).netloc
        host, _, port = netloc.partition(':')
        saml_request = dict(
            http_host=host,
            script_name=request.path,
            get_data={k: v[0] if len(v) == 1 else v for k, v in request.query_arguments.items()},
            post_data={k: v[0] if len(v) == 1 else v for k, v in request.body_arguments.items()}
        )

        if port:
            saml_request['server_port'] = port

        saml_settings = Saml2MetadataHandler.get_saml_settings(settings, saml_config)

        raise Return(
            (OneLogin_Saml2_Auth(saml_request, saml_settings), "{0}/api/v1/auth/saml".format(settings["hostname"]))
        )

    def _get_attribute(self, attributes, mappings):
        for mapping in mappings:
            values = attributes.get(mapping, [])
            if len(values) > 0:
                return values[0].encode('utf8')

        return ""

    @coroutine
    def get(self):
        logging.info("Initiating SAML 2.0 Auth.")
        auth, return_to = yield self._get_saml_auth(self.request)

        logging.info("Redirecting to SAML for authentication.")
        self.redirect(auth.login(return_to=return_to))

    @coroutine
    def post(self):
        logging.info("SAML redirect received.")

        auth, _ = yield self._get_saml_auth(self.request)
        auth.process_response()

        errors = auth.get_errors()
        if len(errors) > 0:
            logging.info("SAML authentication error: '%s'.", auth.get_last_error_reason())
            raise HTTPError(401, reason=auth.get_last_error_reason())

        if not auth.is_authenticated():
            logging.info("SAML user not authenticated.")
            raise HTTPError(401, reason="SAML user not authenticated.")

        attributes = auth.get_attributes()
        logging.debug('SAML Attributes received: {0}'.format(attributes))
        first_name = self._get_attribute(attributes, self.FIRST_NAME_ATTRIBUTES)
        last_name = self._get_attribute(attributes, self.LAST_NAME_ATTRIBUTES)

        settings = yield Query(self.settings["database"], "Settings").find_one()
        saml = settings[u'authentication'].get('saml', None)

        name_id = auth.get_nameid()
        user_email = self._get_attribute(attributes, self.EMAIL_ATTRIBUTES).lower()
        if not user_email:
            raise HTTPError(401, reason="SAML email attribute is missing.")

        user = yield self.settings["database"].Users.find_one({"saml_id": name_id})
        user_updated = False
        if user and user["email"] != user_email:
            logging.info("User email changed!")
            user["email"] = user_email
            user_updated = True
        elif not user:
            user = yield self.settings["database"].Users.find_one({"email": re.compile(user_email, re.IGNORECASE)})
            if user:
                user["saml_id"] = name_id
                user_updated = True

        # Validate user if it signup by SAML
        if user and 'email_validated_at' not in user:
            logging.debug('User %s (%s) validated via SAML', user_email, name_id)
            user = yield self._update_invited_user(user, attributes)
            user_updated = True

        if user:
            if user_updated:
                user = yield Query(self.settings["database"], 'Users').update(user)
            yield self.authenticate_user(user)
            self.redirect('/')
        else:
            logging.debug("User '%s' (%s) not found", user_email, name_id)
            escaped_name = cgi.escape("{0} {1}".format(first_name, last_name), quote=True)
            if not escaped_name:
                escaped_name = cgi.escape(name_id, quote=True)

            self.redirect('/request-invite?account={0}&&name={1}'.format(
                cgi.escape(user_email, quote=True),
                escaped_name))

    @coroutine
    def _update_invited_user(self, user, attributes):
        for namespace_name in user["namespaces"]:
            namespace = yield Query(self.settings["database"], "Namespaces").find_one({"name": namespace_name})
            if namespace is None:
                logging.warn("Cannot find namespace %s", namespace_name)
            else:
                if "members" in namespace:
                    namespace["members"].append(user["username"])
                else:
                    namespace["members"] = [user["username"]]

                yield Query(self.settings["database"], "Namespaces").update(namespace)

        del user["namespaces"]

        first_name = self._get_attribute(attributes, self.FIRST_NAME_ATTRIBUTES)
        last_name = self._get_attribute(attributes, self.LAST_NAME_ATTRIBUTES)
        _fill_signup_invitation_request(user, firstname=first_name, lastname=last_name, password=None)

        raise Return(user)
