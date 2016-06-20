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

class NamespacesSelectorController {

    constructor($q, $scope, $state, instancesNavigationActionCreator, chartsNavigationActionCreator, sessionStore, namespacesStore,
                sessionActionCreator) {
        'ngInject';

        const onChange = () => {
            this.namespaces = _.sortBy(this._namespacesStoreService.getAll(), 'metadata.name');
            this.namespace = _.find(this.namespaces, _.matchesProperty('metadata.uid', this.namespace.metadata.uid)) || this.namespaces[0];
        };
        const onNamespaceChange = () => this.namespace = this._sessionStoreService.getActiveNamespace();

        this._$q = $q;
        this._$state = $state;
        this._instancesNavigationActionCreator = instancesNavigationActionCreator;
        this._chartsNavigationActionCreator = chartsNavigationActionCreator;
        this._namespacesStoreService = namespacesStore;
        this._sessionStoreService = sessionStore;
        this._sessionActionCreator = sessionActionCreator;

        this._sessionStoreService.addNamespaceChangeListener(onNamespaceChange);
        this._namespacesStoreService.addChangeListener(onChange);

        this.namespaces = _.sortBy(this._namespacesStoreService.getAll(), 'metadata.name');
        this.namespace = this._sessionStoreService.getActiveNamespace();

        $scope.$on('$destroy', () => {
            this._namespacesStoreService.removeChangeListener(onChange);
            this._sessionStoreService.removeNamespaceChangeListener(onNamespaceChange);
        });
    }

    namespaceSelected() {
        return this._sessionActionCreator.selectNamespace(this.namespace)
            .then(() => {
                switch (this._$state.current.name) {

                    case 'instance':
                    case 'instances':
                        return this._instancesNavigationActionCreator.instances();

                    case 'charts':
                        return this._chartsNavigationActionCreator.charts();

                    default:
                        return this._$q.when();
                }
            });
    }
}

export default NamespacesSelectorController;
