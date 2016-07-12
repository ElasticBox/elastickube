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
import defaultPasswordRegexString from 'text!../../../../api/resources/password_default_regex';

class SignupController {
    constructor($log, $scope, adminNavigationActionCreator, initialization, usersActionCreator) {
        'ngInject';

        this._$log = $log.getInstance(this.constructor.name);
        this._$scope = $scope;
        this._adminNavigationActionCreator = adminNavigationActionCreator;
        this._initialization = initialization;
        this._usersActionCreator = usersActionCreator;

        this.PASSWORD_REGEX = new RegExp(defaultPasswordRegexString.trim());
    }

    submit() {
        return this._usersActionCreator.signup(this._$scope.user)
            .then(() => this._initialization.initializeLoggedInUser())
            .then(() => this._adminNavigationActionCreator.settings())
            .catch((response) => {
                switch (response.status) {
                    case constants.httpStatusCode.BAD_REQUEST:
                        this._$log.error(response.body);
                        break;
                    case constants.httpStatusCode.FORBIDDEN:
                        this._$log.warn(response.body);
                        break;
                    default:
                }
            });
    }
}

export default SignupController;
