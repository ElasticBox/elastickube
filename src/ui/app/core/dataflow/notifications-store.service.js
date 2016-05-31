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
        this._namespacesUnread = [];
        this._totalUnread = 0;

        this.dispatchToken = dispatcher.register((action) => {
            switch (action.type) {

                case this._actions.NOTIFICATIONS_SUBSCRIBED:
                    this._setNotifications(action.notifications);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATION_UPDATED:
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATIONS_UPDATED:
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATIONS_LOADED:
                    this._loadedOldNotifications(action.notifications);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATIONS_VIEWED:
                    this._totalUnread = 0;
                    this._namespacesUnread = [];
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NOTIFICATION_CREATED:
                case this._actions.NOTIFICATIONS_CREATED:
                    this._setNotification(action.notification);
                    this.emit(CHANGE_EVENT);
                    break;

                default:
            }
        });
    }

    _setNotifications(notifications) {
        this._notifications = notifications.latest;
        this._totalUnread = notifications.total_unread;
        this._namespacesUnread = notifications.unread_namespaces;
    }

    _setNotification(notification) {
        const index = _.findIndex(this._notifications, _.pick(notification.notification, '_id'));

        if (index === -1) {
            this._notifications.unshift(notification.notification);
        }
        this._totalUnread = notification.total_unread;
        this._namespacesUnread = notification.unread_namespaces;
    }

    _loadedOldNotifications(notifications) {
        const oldNotifications = _.get(notifications, 'body', []);

        if (oldNotifications.length > 0) {
            if (_.last(this._notifications).metadata.creationTimestamp > oldNotifications[0].metadata.creationTimestamp) {
                this._notifications = this._notifications.concat(oldNotifications);
            }
        }
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

    getCurrentNewestNotification() {
        return _.first(this._notifications);
    }

    getTotalUnreadCount() {
        return this._totalUnread;
    }

    getUnreadNamespace(namespace) {
        const unreadNamespace = _.find(this._namespacesUnread, { name: namespace });

        return unreadNamespace && unreadNamespace.unread;
    }

    addChangeListener(callback) {
        this.on(CHANGE_EVENT, callback);
    }

    removeChangeListener(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
}

export default NotificationsStoreService;
