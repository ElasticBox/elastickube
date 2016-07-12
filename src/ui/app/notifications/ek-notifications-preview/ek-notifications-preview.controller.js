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

const PAGE_SIZE = 5;

class NotificationsPreviewController {
    constructor($filter, $scope, notificationsActionCreator, notificationsNavigationActionCreator, notificationsStore, usersStore) {
        'ngInject';

        const onChange = () => this.notifications = notificationsStore.getAll();

        notificationsStore.addChangeListener(onChange);

        this._humanizeDateFilter = $filter('ekHumanizeDate');
        this._notificationsActionCreator = notificationsActionCreator;
        this._notificationsNavigationActionCreator = notificationsNavigationActionCreator;
        this._notificationsStore = notificationsStore;
        this._usersStore = usersStore;

        this.notifications = notificationsStore.getAll();

        $scope.$on('$destroy', () => notificationsStore.removeChangeListener(onChange));
    }

    getUserName(user) {
        const userInfo = this._usersStore.get(user);

        return userInfo ? `${userInfo.firstname} ${userInfo.lastname}` : '';
    }

    getNotificationState(notification) {
        const user = this._usersStore.getPrincipal();

        return user && notification.metadata.creationTimestamp <= user.notifications_viewed_at ? 'read' : 'new';
    }

    getNotificationActionText(notification) {
        const resource = notification.resource;

        switch (notification.operation) {
            case 'create':
                return resource.kind === 'User' ? 'invited to' : 'created';

            case 'delete':
                return ['Pod', 'ReplicationController', 'Service'].indexOf(resource.kind) !== -1 ? `deleted ${resource.kind}` : 'deleted';

            case 'add':
                return resource.kind === 'User' ? `added ${this.getResourceName(resource)} to` : 'added';

            case 'remove':
                return resource.kind === 'User' ? `removed ${this.getResourceName(resource)} from` : 'removed';

            case 'deploy':
                return 'deployed';

            default:
                return notification.operation;
        }
    }

    getResourceName(resource) {
        switch (resource.kind) {
            case 'User':
                const user = this._usersStore.getPrincipal();

                return user && user.username === resource.name ? 'you' : this.getUserName(resource.name);

            case 'Pod':
            case 'ReplicationController':
            case 'Service':
                return `${resource.kind} ${resource.name}`;

            default:
                return resource.name;
        }
    }

    getTargetResourceName(notification) {
        const resource = notification.resource;

        switch (resource.kind) {
            case 'User':
                return notification.operation === 'create' ? this.getUserName(resource.name) : notification.namespace;

            case 'Pod':
            case 'ReplicationController':
            case 'Service':
                return `${notification.namespace}/${resource.name}`;

            case 'Chart':
                return notification.namespace ? `${notification.namespace}/${resource.name}` : resource.name;

            default:
                return resource.name;
        }
    }

    getUserName(user) {
        const userInfo = this._usersStore.get(user);

        return userInfo ? `${userInfo.firstname} ${userInfo.lastname}` : user;
    }

    loadMore() {
        this._notificationsActionCreator.loadMore(this._notificationsStore.getCurrentOldestNotification(), PAGE_SIZE);
    }

    seeAll() {
        this.headerNotificationCtrl.closeDrop();
        this._notificationsNavigationActionCreator.seeAll();
    }
}

export default NotificationsPreviewController;
