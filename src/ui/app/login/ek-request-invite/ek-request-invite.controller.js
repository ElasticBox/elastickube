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

class RequestInviteController {
    constructor($log, $stateParams, loginNavigationActionCreator, notificationsActionCreator) {
        'ngInject';

        this._$log = $log.getInstance(this.constructor.name);
        this._$stateParams = $stateParams;
        this._loginNavigationActionCreator = loginNavigationActionCreator;
        this._notificationsActionCreator = notificationsActionCreator;
        this.submitting = false;

        if (this._$stateParams.account) {
            this.account = this._$stateParams.account;
            this.name = this._$stateParams.name;
        }
    }

    submit() {
        this.submitting = true;

        return this._notificationsActionCreator
            .requestInvite({
                email: this.account || this.email,
                name: this.name
            })
            .then(() => this._loginNavigationActionCreator.login())
            .catch((error) => this._$log.warn(error.statusText))
            .finally(() => this.submitting = false);
    }
}

export default RequestInviteController;
