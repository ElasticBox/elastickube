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
import constants from './constants';

const NAMESPACE_UPDATED_EVENT = 'namespace.change';
const INSTANCES_STATUS_CHANGED_EVENT = 'instances-status.changed';
const ADMIN_INSTANCES_STATUS_CHANGED_EVENT = 'admin-instances-status.changed';

class SessionStoreService extends AbstractStore {
    constructor(session, actions, dispatcher, namespacesStore) {
        'ngInject';

        super(session);

        this._actions = actions;
        this._session = session;
        this._namespacesStore = namespacesStore;

        this.dispatchToken = dispatcher.register((action) => {
            switch (action.type) {

                case this._actions.SESSION_NAMESPACE_CHANGED:
                    this.emit(NAMESPACE_UPDATED_EVENT);
                    break;

                case this._actions.SESSION_INSTANCES_STATUS_CHANGED:
                    this.emit(INSTANCES_STATUS_CHANGED_EVENT);
                    break;

                case this._actions.SESSION_ADMIN_INSTANCES_STATUS_CHANGED:
                    this.emit(ADMIN_INSTANCES_STATUS_CHANGED_EVENT);
                    break;

                default:
            }
        });
    }

    getActiveNamespace() {
        const namespaceUID = this._session.getItem(constants.ACTIVE_NAMESPACE);

        return _.find(this._namespacesStore.getAll(), (x) => x.metadata.uid === namespaceUID);
    }

    getSessionToken() {
        return this._session.getItem(constants.SESSION_TOKEN);
    }

    getInstancesStatus() {
        const namespaceUID = this._session.getItem(constants.ACTIVE_NAMESPACE);
        const instancesStatus = this._session.getItem(constants.INSTANCES_STATUS) || {};

        return instancesStatus[namespaceUID];
    }

    getAdminInstancesStatus() {
        return this._session.getItem(constants.ADMIN_INSTANCES_STATUS);
    }

    setInitialState(name, params) {
        this._session.setItem(constants.INITIAL_STATE, JSON.stringify({
            name,
            params
        }));
    }

    getInitialState() {
        return this._session.getItem(constants.INITIAL_STATE) && JSON.parse(this._session.getItem(constants.INITIAL_STATE));
    }

    removeInitialState() {
        return this._session.removeItem(constants.INITIAL_STATE);
    }

    addNamespaceChangeListener(callback) {
        this.on(NAMESPACE_UPDATED_EVENT, callback);
    }

    removeNamespaceChangeListener(callback) {
        this.removeListener(NAMESPACE_UPDATED_EVENT, callback);
    }

    addInstancesStatusChangeListener(callback) {
        this.on(INSTANCES_STATUS_CHANGED_EVENT, callback);
    }

    removeInstancesStatusChangeListener(callback) {
        this.removeListener(INSTANCES_STATUS_CHANGED_EVENT, callback);
    }

    addAdminInstancesStatusChangeListener(callback) {
        this.on(ADMIN_INSTANCES_STATUS_CHANGED_EVENT, callback);
    }

    removeAdminInstancesStatusChangeListener(callback) {
        this.removeListener(ADMIN_INSTANCES_STATUS_CHANGED_EVENT, callback);
    }
}

export default SessionStoreService;
