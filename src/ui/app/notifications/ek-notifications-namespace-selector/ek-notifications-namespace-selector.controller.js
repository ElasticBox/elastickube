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

class NotificationsNamespaceSelectorController {
    constructor($scope, namespacesStore, notificationsStore) {
        'ngInject';

        const onNamespacesChange = () => {
            this.namespaces = _.chain(namespacesStore.getAll())
                .map((namespace) => _.get(namespace, 'metadata.name'))
                .value().sort();

            this.namespaces.unshift('All');
            this.notifications = notificationsStore.getAll();
        };
        const onNotificationsChange = () => {
            this.notifications = notificationsStore.getAll();
        };

        this._namespacesStore = namespacesStore;

        namespacesStore.addChangeListener(onNamespacesChange);
        notificationsStore.addChangeListener(onNotificationsChange);

        this._notificationsStore = notificationsStore;

        this.namespaces = _.chain(namespacesStore.getAll())
            .map((namespace) => _.get(namespace, 'metadata.name'))
            .value().sort();

        this.namespaces.unshift('All');

        this.notifications = notificationsStore.getAll();

        this.selectedNamespace = _.first(this.namespaces);

        $scope.$on('$destroy', () => {
            namespacesStore.removeChangeListener(onNamespacesChange);
            notificationsStore.removeChangeListener(onNotificationsChange);
        });
    }

    selectNamespace(namespace) {
        this.selectedNamespace = namespace;
    }

    unreadNamespace(namespace) {
        const unread = namespace === 'All'
            ? this._notificationsStore.getTotalUnreadCount()
            : this._notificationsStore.getUnreadNamespace(namespace);

        return unread > 0 ? unread : '';
    }
}

function countNamespaces(notifications) {
    return _.chain(notifications)
        .groupBy('namespace')
        .mapValues((x) => x.length)
        .value();
}

export default NotificationsNamespaceSelectorController;
