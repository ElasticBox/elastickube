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

class NamespacesStoreService extends AbstractStore {
    constructor($q, session, actions, dispatcher) {
        'ngInject';

        super(session);

        this._$q = $q;
        this._actions = actions;
        this._namespaces = {};

        this.dispatchToken = dispatcher.register((action) => {
            switch (action.type) {

                case this._actions.NAMESPACES_SUBSCRIBE:
                    this._isLoading = this._$q.defer();
                    break;

                case this._actions.NAMESPACES_SUBSCRIBED:
                    this._setNamespaces(action.namespaces);
                    this._isLoading.resolve();
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NAMESPACES_CREATED:
                    this._setNamespace(action.namespace);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NAMESPACES_UPDATED:
                    this._setNamespace(action.namespace);
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.NAMESPACES_DELETED:
                    this._removeNamespace(action.namespace);
                    this.emit(CHANGE_EVENT);
                    break;

                default:
            }
        });
    }

    _setNamespace(namespace) {
        if (namespace) {
            this._namespaces[namespace.metadata.uid] = namespace;
        }
    }

    _setNamespaces(namespaces) {
        const newNamespaces = {};

        _.each(namespaces, (x) => newNamespaces[x.metadata.uid] = x);

        this._namespaces = newNamespaces;
    }

    _removeNamespace(namespace) {
        delete this._namespaces[namespace._id];
    }

    destroy() {
        this._namespaces = {};
        delete this._isLoading;
    }

    getAll() {
        return _.values(this._namespaces);
    }

    get(uid) {
        return this._namespaces[uid];
    }

    isLoading() {
        return this._isLoading.promise;
    }

    addChangeListener(callback) {
        this.on(CHANGE_EVENT, callback);
    }

    removeChangeListener(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
}

export default NamespacesStoreService;
