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
            const date = notification.date.isSame(moment(), 'day') ? 'Today' : notification.date.format('MM/DD/YY');

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

    getNotificationDate(notification) {
        return this._humanizeDateFilter(notification.date);
    }

    getUserName(user) {
        const userInfo = this._usersStore.get(user);

        return userInfo ? `${userInfo.firstname} ${userInfo.lastname}` : '';
    }
}

export default NotificationsListController;
