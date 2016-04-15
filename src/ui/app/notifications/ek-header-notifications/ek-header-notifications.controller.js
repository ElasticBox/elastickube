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

class HeaderNotificationsController {
    constructor($scope, notificationsActionCreator, notificationsStore) {
        'ngInject';

        const onChange = () => this.totalUnread = this._getNotificationCount();

        this._notificationsStore = notificationsStore;
        this._notificationsActionCreator = notificationsActionCreator;

        notificationsStore.addChangeListener(onChange);
        this.closed = true;

        this.totalUnread = this._getNotificationCount();
        $scope.$on('$destroy', () => notificationsStore.removeChangeListener(onChange));

        this._onDropClose = () => {
            this.closed = true;
            return this.settingsVisible && this.showSettings() || this.closed;
        };
    }

    _getNotificationCount() {
        const unreadNotifications = this._notificationsStore.getTotalUnreadCount();

        return unreadNotifications < 100 ? unreadNotifications : '+99';
    }

    markAllAsSeen() {
        this.closed = !this.closed;
        if (this.totalUnread !== 0 && !this.closed) {
            this._notificationsActionCreator.changeNotificationsState('seen');
        }
    }

    closeDrop() {
        this.drop.close();
    }

    showSettings() {
        const settingsDOMElement = angular.element('.ek-header-notifications__drop__content__container__settings');

        this.settingsVisible = !this.settingsVisible;

        if (this.settingsVisible) {
            settingsDOMElement.addClass('ek-header-notifications__drop__content__container__settings--visible');
        } else {
            settingsDOMElement.removeClass('ek-header-notifications__drop__content__container__settings--visible');
        }
    }
}

export default HeaderNotificationsController;
