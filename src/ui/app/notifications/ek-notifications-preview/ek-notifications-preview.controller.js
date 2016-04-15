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

        this._humanizeDateFilter = $filter('ekHumanizeDate');
        this._notificationsActionCreator = notificationsActionCreator;
        this._notificationsNavigationActionCreator = notificationsNavigationActionCreator;
        this._notificationsStore = notificationsStore;
        this._usersStore = usersStore;
        notificationsStore.addChangeListener(onChange);

        this.notifications = notificationsStore.getAll();
        $scope.$on('$destroy', () => notificationsStore.removeChangeListener(onChange));
    }

    getNotificationDate(notification) {
        return this._humanizeDateFilter(notification.date);
    }

    getUserName(user) {
        const userInfo = this._usersStore.get(user);

        return userInfo ? `${userInfo.firstname} ${userInfo.lastname}` : '';
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
