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

class InitializationService {

    /* eslint max-params: 0 */
    constructor($q, $cookies, chartsActionCreator, instancesAPI, namespacesActionCreator, namespacesStore,
                notificationsActionCreator, sessionActionCreator, sessionStore, usersActionCreator, websocketClient) {
        'ngInject';

        this._$q = $q;
        this._$cookies = $cookies;
        this._chartsActionCreator = chartsActionCreator;
        this._instancesAPI = instancesAPI;
        this._namespacesActionCreator = namespacesActionCreator;
        this._namespacesStore = namespacesStore;
        this._notificationsActionCreator = notificationsActionCreator;
        this._sessionActionCreator = sessionActionCreator;
        this._sessionStore = sessionStore;
        this._usersActionCreator = usersActionCreator;
        this._websocketClient = websocketClient;

        this.deferred = $q.defer();
        this.initialized = false;
    }

    initializeUnloggedUser() {
        return this._sessionActionCreator.destroy()
            .then(() => {
                if (!this.initialized) {
                    this.initialized = true;
                    this.deferred.resolve();
                }
            });
    }

    initializeLoggedInUser() {
        const sessionToken = this._$cookies.get(constants.SESSION_TOKEN_NAME);
        const sessionDestroyed = sessionToken !== this._sessionStore.getSessionToken()
            ? this._sessionActionCreator.destroy().then(() => this._sessionActionCreator.storeSessionToken(sessionToken))
            : false;

        const tokenData = JSON.parse(atob(sessionToken.split('.')[1]));

        return this._$q.when(sessionDestroyed)
            .then(() => this._websocketClient.connect())
            .then(() => this._instancesAPI.initializeSubscriptions())
            .then(() => this._chartsActionCreator.subscribe())
            .then(() => this._namespacesActionCreator.subscribe())
            .then(() => this._notificationsActionCreator.subscribe())
            .then(() => this._usersActionCreator.subscribe())
            .then(() => this._usersActionCreator.loggedIn(tokenData.username))
            .then(() => {
                let namespace = this._sessionStore.getActiveNamespace();

                if (_.isUndefined(namespace)) {
                    namespace = _.chain(this._namespacesStore.getAll())
                        .first()
                        .value();
                }

                return this._sessionActionCreator.selectNamespace(namespace);
            })
            .then(() => {
                if (!this.initialized) {
                    this.initialized = true;
                    this.deferred.resolve();
                }
            });
    }
}

export default InitializationService;
