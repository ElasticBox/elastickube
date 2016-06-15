/*
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
*/

import constants from 'constants';
import profiles from './profiles';

class AuthService {
    constructor($cookies, initialization, loginNavigationActionCreator, usersStore, routerHelper,
                sessionActionCreator, sessionStore, websocketClient) {
        'ngInject';
        let sessionToken = $cookies.get(constants.SESSION_TOKEN_NAME);

        this._$cookies = $cookies;
        this._loginNavigationActionCreator = loginNavigationActionCreator;
        this._usersStore = usersStore;
        this._routerHelper = routerHelper;
        this._sessionActionCreator = sessionActionCreator;
        this._sessionStore = sessionStore;
        this._websocketClient = websocketClient;

        websocketClient.addErrorEventListener(() => initialization.initializeUnloggedUser()
            .then(() => this.logout()));

        if (_.isUndefined(sessionToken)) {
            sessionToken = this._sessionStore.getSessionToken();

            if (_.isUndefined(sessionToken)) {
                initialization.initializeUnloggedUser();
            } else {
                $cookies.put(constants.SESSION_TOKEN_NAME, sessionToken, { secure: false });
                initialization.initializeLoggedInUser();
            }
        } else {
            initialization.initializeLoggedInUser();
        }
    }

    isLoggedIn() {
        return !_.isUndefined(this._usersStore.getPrincipal());
    }

    isAdmin() {
        return this._usersStore.isAdmin();
    }

    logout() {
        this._$cookies.remove(constants.SESSION_TOKEN_NAME);

        return this._sessionActionCreator.destroy()
            .then(() => this._websocketClient.disconnect())
            .then(() => this._loginNavigationActionCreator.login());
    }

    authorize(access) {
        switch (access) {
            case profiles.ADMIN:
                return this.isAdmin();
            case profiles.PRIVATE:
                return this.isLoggedIn();
            default:
                return !this.isLoggedIn();
        }
    }
}

export default AuthService;
