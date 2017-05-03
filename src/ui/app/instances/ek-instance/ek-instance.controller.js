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

class InstanceController {
    constructor($q, $scope, $state, $stateParams, instancesNavigationActionCreator, instanceStore) {
        'ngInject';

        const onChange = () => this._updateInstance();

        this._$q = $q;
        this._$state = $state;
        this._$stateParams = $stateParams;
        this._instancesNavigationActionCreator = instancesNavigationActionCreator;
        this._instanceStore = instanceStore;

        this._updateInstance();
        this.tab = _.last($state.current.name.split('.'));

        instanceStore.addChangeListener(onChange);

        $scope.$on('$destroy', () => instanceStore.removeChangeListener(onChange));
    }

    _updateInstance() {
        this.instance = this._instanceStore.getInstance();

        if (_.isUndefined(this.instance)) {
            return this._instancesNavigationActionCreator.instances();
        }
        return this._$q.when();
    }

    selectTab(tabName = 'overview') {
        const tabs = this.instance.kind === 'Pod' ? ['overview', 'events', 'containers'] : ['overview'];

        if (_.includes(tabs, tabName)) {
            this.tab = tabName;

            const namespace = this._$stateParams.namespace;
            const instanceId = this._$stateParams.instanceId;

            switch (tabName) {
                case 'events':
                    return this._instancesNavigationActionCreator.instanceEvents({ namespace, instanceId });
                case 'containers':
                    return this._instancesNavigationActionCreator.instanceContainers({ namespace, instanceId });
                default:
                    return this._instancesNavigationActionCreator.instance({ namespace, instanceId });
            }
        }
        return this._$q.when();
    }
}

export default InstanceController;
