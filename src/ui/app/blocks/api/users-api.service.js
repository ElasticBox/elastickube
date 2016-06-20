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

import AbstractAPI from './abstract-api';

class UsersAPIService extends AbstractAPI {

    constructor($http, websocketClient) {
        'ngInject';

        super('users', websocketClient);

        this._$http = $http;
    }

    signup(user, code) {
        const options = {
            headers: {
                'ElasticKube-Validation-Token': code
            }
        };

        /* eslint no-undefined: 0 */
        return this._$http.post('api/v1/auth/signup', user, code ? options : undefined);
    }

    login(user) {
        return this._$http.post('api/v1/auth/login', user);
    }
}

export default UsersAPIService;
