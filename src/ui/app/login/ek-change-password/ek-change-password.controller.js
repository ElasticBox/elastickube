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

class ChangePasswordController {
    constructor($log, $location, loginNavigationActionCreator, notificationsActionCreator) {
        'ngInject';

        this._$log = $log;
        this._$location = $location;

        this._loginNavigationActionCreator = loginNavigationActionCreator;
        this._notificationsActionCreator = notificationsActionCreator;

        this.PASSWORD_REGEX = new RegExp(this.authProviders.password.regex);
    }

    submit() {
        return this._notificationsActionCreator
            .changePassword({
                password: this.password,
                token: Object.keys(this._$location.search())[0]
            })
            .then(() => this._loginNavigationActionCreator.login())
            .catch((error) => this._$log.warn(error.statusText));
    }
}

export default ChangePasswordController;
