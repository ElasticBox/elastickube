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

class NotificationsListController {
    constructor($scope, $timeout, notificationsStore, notificationsActionCreator) {
        'ngInject';

        const onChange = () => this.notifications = notificationsStore.getAll();

        this._$timeout = $timeout;
        this._notificationsStore = notificationsStore;
        this._notificationsActionCreator = notificationsActionCreator;

        notificationsStore.addChangeListener(onChange);

        this.notifications = notificationsStore.getAll();
        this.showEmpty = true;

        $scope.$watchCollection('ctrl.notificationsFilteredByNamespace', (x) => this.showEmpty = _.isEmpty(x));

        $scope.$on('$destroy', () => {
            notificationsStore.removeChangeListener(onChange);
            this._markAllAsSeen();
        });
    }

    _markAllAsSeen() {
        if (this._notificationsStore.getTotalUnreadCount() > 0) {
            this._notificationsActionCreator.changeNotificationsState('seen');
        }
    }

    markAllAsRead() {
        this._notificationsActionCreator.changeNotificationsState('read');
    }

    loadMore() {
        this._notificationsActionCreator.loadMore(this._notificationsStore.getCurrentOldestNotification(), PAGE_SIZE);
    }
}

export default NotificationsListController;
