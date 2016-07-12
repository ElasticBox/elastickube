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

class CheckNamespaceService {
    constructor($q, $stateParams, instancesNavigationActionCreator, namespacesStore, sessionActionCreator, sessionStore) {
        'ngInject';

        this._$q = $q;

        this._$stateParams = $stateParams;
        this._instancesNavigationActionCreator = instancesNavigationActionCreator;
        this._namespacesStore = namespacesStore;
        this._sessionActionCreator = sessionActionCreator;
        this._sessionStore = sessionStore;
    }

    execute() {
        let namespace = this._$stateParams.namespace;

        if (!_.isUndefined(namespace)) {
            namespace = _.find(this._namespacesStore.getAll(), _.matchesProperty('metadata.name', namespace));

            if (_.isUndefined(namespace)) {
                return this._instancesNavigationActionCreator.instances();
            } else if (namespace !== this._sessionStore.getActiveNamespace()) {
                return this._sessionActionCreator.selectNamespace(namespace);
            }
        }

        return this._$q.when();
    }
}

export default CheckNamespaceService;
