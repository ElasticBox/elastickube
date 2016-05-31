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

class NotificationsActionCreatorService {
    constructor($q, actions, dispatcher, notificationsAPI) {
        'ngInject';

        this._$q = $q;

        this._actions = actions;
        this._notificationsAPI = notificationsAPI;
        this._dispatcher = dispatcher;

        notificationsAPI.addOnCreatedListener((notification) => this._dispatcher.dispatch(
            { type: this._actions.NOTIFICATION_CREATED, notification })
        );
        notificationsAPI.addOnUpdatedListener(() => this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_UPDATED }));
    }

    subscribe() {
        this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_SUBSCRIBE });

        return this._notificationsAPI.subscribe()
            .then((notifications) => this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_SUBSCRIBED, notifications }));
    }

    loadMore(lastNotification, pageSize) {
        const LoadMoreNotificationsBody = {
            lastNotification,
            pageSize
        };

        this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_LOAD });

        return this._notificationsAPI.loadMore(LoadMoreNotificationsBody)
            .then((notifications) => this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_LOADED, notifications }));
    }

    view(timestamp) {
        this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_VIEW });

        return this._notificationsAPI.view(timestamp)
            .then(() => this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_VIEWED }));
    }

    emailSetting(timestamp) {
        this._dispatcher.dispatch({ type: this._actions.NOTIFICATIONS_UPDATE });

        return this._notificationsAPI.emailSetting(timestamp);
    }

}

export default NotificationsActionCreatorService;
