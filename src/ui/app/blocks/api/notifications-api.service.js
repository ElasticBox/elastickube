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

class NotificationsAPIService extends AbstractAPI {

    constructor($q, websocketClient) {
        'ngInject';

        super('notifications', websocketClient);

        this._$q = $q;
        this._websocketClient = websocketClient;
    }

    loadMore(body) {
        const message = {
            action: 'notifications',
            body,
            operation: 'retrieve'
        };

        return this._$q.when(this._websocketClient.sendMessage(message));
    }

    view(timestamp) {
        const message = {
            action: 'notifications',
            body: { viewed_at: timestamp },
            operation: 'update'
        };

        return this._$q.when(this._websocketClient.sendMessage(message));
    }

    emailSetting(reciveEmails) {
        const message = {
            action: 'notifications',
            body: { email_notifications: reciveEmails },
            operation: 'update'
        };

        return this._$q.when(this._websocketClient.sendMessage(message));
    }

}

export default NotificationsAPIService;
