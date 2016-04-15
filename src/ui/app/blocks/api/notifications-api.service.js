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
import moment from 'moment';

const totalUnread = 4;
const notificationsMocks = {
    totalUnread,
    notifications: [{
        id: 1,
        user: 'paulino@elasticbox.com',
        state: 'new',
        description: 'added you to elasticbox',
        kind: 'namespace',
        namespace: 'default',
        date: moment().subtract(1, 'hour')
    }, {
        id: 2,
        user: 'paulino@elasticbox.com',
        state: 'new',
        description: 'deleted engineering/kube-dns',
        kind: 'delete',
        namespace: 'default',
        date: moment().subtract(1, 'days')
    }, {
        id: 3,
        user: 'paulino@elasticbox.com',
        state: 'new',
        description: 'deployed engineering/kube-dns',
        kind: 'deploy',
        namespace: 'default',
        date: moment().subtract(2, 'days')
    }, {
        id: 4,
        user: 'paulino@elasticbox.com',
        state: 'read',
        description: 'removed you from test',
        kind: 'namespace',
        namespace: 'kube-system',
        date: moment().subtract(3, 'days')
    }, {
        id: 5,
        user: 'paulino@elasticbox.com',
        state: 'seen',
        description: 'deployed engineering/elastickube-mongo-fw36o',
        kind: 'deploy',
        namespace: 'default',
        date: moment().subtract(3, 'days')
    }, {
        id: 6,
        user: 'paulino@elasticbox.com',
        state: 'new',
        description: 'added you to Engineering',
        kind: 'namespace',
        namespace: 'kube-system',
        date: moment().subtract(4, 'days')
    }, {
        id: 7,
        user: 'paulino@elasticbox.com',
        state: 'read',
        description: 'deployed engineering/elastickube-api-fw36o',
        kind: 'deploy',
        namespace: 'kube-system',
        date: moment().subtract(4, 'days')
    }]
};

class NotificationsAPIService extends AbstractAPI {

    constructor($q, websocketClient) {
        'ngInject';

        super('notifications', websocketClient);

        this._$q = $q;
    }

    loadMore(body) {
        const notifications = [];

        for (let i = 0; i < 5; i++) {
            notifications.push({
                id: Date.now() + i,
                user: 'paulino@elasticbox.com',
                state: 'read',
                description: `deployed engineering-${i}`,
                kind: 'deploy',
                date: moment().subtract(4, 'days')
            });
        }

        return this._$q.when({ totalUnread, notifications });
    }

    subscribe() {
        return this._$q.when(notificationsMocks);
    }

    update() {
        return this._$q.when();
    }
}

export default NotificationsAPIService;
