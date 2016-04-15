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

import AbstractStore from './abstract-store';

const CHANGE_EVENT = 'change';

class NotificationsStoreService extends AbstractStore {
    constructor(session, actions, dispatcher) {
        'ngInject';

        super(session);

        this._actions = actions;
        this._notifications = [];

        this.dispatchToken = dispatcher.register((action) => {
            switch (action.type) {

                case this._actions.NOTIFICATIONS_SUBSCRIBED:
                    this._setNotifications(action.notifications);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATION_UPDATED:
                    this._setNotification(action.notification);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATIONS_UPDATED:
                    this._setNotificationState(action.state);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATIONS_LOADED:
                    this._loadedOldNotifications(action.notifications);
                    this.emit(CHANGE_EVENT);
                    break;

                default:
            }
        });
    }

    _setNotifications(notifications) {
        this._notifications = notifications.notifications;
        this._totalUnread = notifications.totalUnread;
    }

    _setNotification(notification) {
        const index = _.findIndex(this._notifications, _.pick(notification.notification, 'id'));

        if (index !== -1) {
            this._notifications.splice(index, 1, notification.notification);
        }
        this._totalUnread = notification.totalUnread;
    }

    _setNotificationState(state) {
        _.each(this._notifications, (notification) => {
            if (state === 'read') {
                notification.state = 'read';
            } else if (notification.state === 'new') {
                notification.state = 'seen';
            }
        });
        this._totalUnread = 0;
    }

    _loadedOldNotifications(oldNotifications) {
        this._notifications = this._notifications.concat(oldNotifications.notifications);
        this._totalUnread = oldNotifications.totalUnread;
    }

    getAll() {
        return this._notifications;
    }

    getUnreadNotifications() {
        return _.filter(this._notifications, (notification) => notification.state === 'new' || notification.state === 'seen');
    }

    getCurrentOldestNotification() {
        return _.last(this._notifications);
    }

    getTotalUnreadCount() {
        return this._totalUnread;
    }

    addChangeListener(callback) {
        this.on(CHANGE_EVENT, callback);
    }

    removeChangeListener(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
}

export default NotificationsStoreService;
