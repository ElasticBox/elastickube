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

import moment from 'moment';

class NotificationsListController {
    constructor($filter, $scope, usersStore) {
        'ngInject';

        this._usersStore = usersStore;

        this._humanizeDateFilter = $filter('ekHumanizeDate');

        $scope.$watchCollection('ctrl.notifications', (notifications) => this.notificationGroups = this.groupNotifications(notifications));
    }

    groupNotifications(notifications) {
        let current;

        return _.reduce(notifications, (result, notification) => {
            const notificationMoment = moment.unix(notification.metadata.creationTimestamp).local();
            const date = notificationMoment.isSame(moment(), 'day') ? 'Today' : notificationMoment.format('MM/DD/YY');

            if (_.isUndefined(current) || date !== current.date) {
                current = {
                    date,
                    notifications: [notification]
                };
                result.push(current);
            } else {
                current.notifications.push(notification);
            }

            return result;
        }, []);
    }

    getNotificationState(notification) {
        return notification.metadata.creationTimestamp <= this._usersStore.getPrincipal().notifications_viewed_at ? 'read' : 'new';
    }

    getNotificationActionText(notification) {
        const resource = notification.resource;

        switch (notification.operation) {
            case 'create':
                return 'created';

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
                return this._usersStore.getPrincipal().username === resource.name ? 'you' : this.getUserName(resource.name);

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
                return notification.namespace;

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
}

export default NotificationsListController;
