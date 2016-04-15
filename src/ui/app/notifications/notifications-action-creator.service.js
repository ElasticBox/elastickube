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

class NavigationActionCreatorService {
    constructor(routerHelper) {
        'ngInject';

        this._routerHelper = routerHelper;
    }

    seeAll() {
        return this._routerHelper.changeToState('notifications');
    }

    resetPassword(email) {
        return this._$http.post('api/v1/auth/reset-password', email);
    }

    changePassword(newPassword) {
        return this._$http.post('api/v1/auth/change-password', newPassword);
    }
}

export default NavigationActionCreatorService;
