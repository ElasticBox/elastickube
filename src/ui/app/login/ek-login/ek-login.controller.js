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

class LoginController {
    constructor($location, $log, $scope, initialization, instancesNavigationActionCreator,
    loginNavigationActionCreator, principalActionCreator, routerHelper, sessionStore) {
        'ngInject';

        this._$location = $location;
        this._$log = $log.getInstance(this.constructor.name);
        this._$scope = $scope;
        this._initialization = initialization;
        this._instancesNavigationActionCreator = instancesNavigationActionCreator;
        this._loginNavigationActionCreator = loginNavigationActionCreator;
        this._principalActionCreator = principalActionCreator;
        this._routerHelper = routerHelper;
        this._sessionStore = sessionStore;
    }

    submit() {
        return this._usersActionCreator.login(this.user)
            .then(() => this._initialization.initializeLoggedInUser())
            .then(() => {
                const _initialState = this._sessionStore.getInitialState();

                if (_initialState) {
                    this._sessionStore.removeInitialState();
                    this._routerHelper.changeToState(_initialState.name, _initialState.params);
                } else {
                    this._instancesNavigationActionCreator.instances();
                }
            })
            .catch((error) => {
                if (error.status === 302) {
                    this._$location.path(error.statusText);
                } else {
                    this._$log.warn(error.statusText || error);
                }
            });
    }

    resetPassword() {
        this._loginNavigationActionCreator.resetPassword();
    }
}

export default LoginController;
