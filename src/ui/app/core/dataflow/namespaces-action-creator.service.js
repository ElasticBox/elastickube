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

class NamespacesActionCreatorService {
    constructor(actions, confirmDialog, dispatcher, namespacesAPI) {
        'ngInject';

        this._actions = actions;
        this._confirmDialog = confirmDialog;
        this._namespacesAPI = namespacesAPI;
        this._dispatcher = dispatcher;

        namespacesAPI.addOnCreatedListener((namespace) => this._dispatcher.dispatch({ type: this._actions.NAMESPACES_CREATED, namespace }));
        namespacesAPI.addOnUpdatedListener((namespace) => this._dispatcher.dispatch({ type: this._actions.NAMESPACES_UPDATED, namespace }));
        namespacesAPI.addOnDeletedListener((namespace) => this._dispatcher.dispatch({ type: this._actions.NAMESPACES_DELETED, namespace }));
    }

    subscribe() {
        this._dispatcher.dispatch({ type: this._actions.NAMESPACES_SUBSCRIBE });

        return this._namespacesAPI.subscribe()
            .then((namespaces) => this._dispatcher.dispatch({ type: this._actions.NAMESPACES_SUBSCRIBED, namespaces }));
    }

    createNamespace(namespaceInfo) {
        const createBody = {
            name: namespaceInfo.namespaceName,
            metadata: {
                labels: namespaceInfo.labels
            },
            members: _.map(namespaceInfo.users, 'username')
        };

        this._dispatcher.dispatch({ type: this._actions.NAMESPACES_CREATE });

        return this._namespacesAPI.create(createBody)
            .then((namespace) => this._dispatcher.dispatch({ type: this._actions.NAMESPACES_CREATED, namespace }));
    }

    updateNamespace(namespace, users) {
        const updateBody = {
            _id: _.get(namespace, 'metadata.uid'),
            members: _.map(users, 'username')
        };

        return this._namespacesAPI.update(updateBody);
    }
}

export default NamespacesActionCreatorService;
