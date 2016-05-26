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

class DashboardController {
    constructor($scope, $timeout, instancesStore, metricsActionCreator, metricsStore, sessionStore) {
        'ngInject';

        const onChange = () => {
            const previousNamespace = this.namespace;

            this.namespace = this._sessionStore.getActiveNamespace();
            $timeout(() => this._metricsActionCreator.unsubscribe(previousNamespace)
                .then(() => this._metricsActionCreator.subscribe(this.namespace)));
            this._getData();
        };

        const metricsChange = () => {
            this.metricsData = this._metricsStore.getMetrics();
        };

        this._instancesStore = instancesStore;
        this._metricsActionCreator = metricsActionCreator;
        this._metricsStore = metricsStore;
        this._sessionStore = sessionStore;

        this.namespace = this._sessionStore.getActiveNamespace();

        this._sessionStore.addNamespaceChangeListener(onChange);
        this._metricsStore.addChangeListener(metricsChange);
        this._metricsActionCreator.subscribe(this.namespace);
        this._getData();

        $scope.$on('$destroy', () => {
            this._metricsActionCreator.unsubscribe(this.namespace);
            this._metricsStore.removeChangeListener(metricsChange);
            this._sessionStore.removeNamespaceChangeListener(onChange);
        });
    }

    _getData() {
        const instances = this._instancesStore.getAll(this.namespace.name);

        this.statistics = {};
        instances.forEach((instance) => {
            switch (instance.kind) {
                case 'Service':
                    if (_.isUndefined(this.statistics.services)) {
                        this.statistics.services = {
                            total: 0
                        };
                    }
                    this.statistics.services.total++;
                    break;

                case 'ReplicationController':
                    if (_.isUndefined(this.statistics.replicationControllers)) {
                        this.statistics.replicationControllers = {
                            total: 0,
                            replicas: 0
                        };
                    }
                    this.statistics.replicationControllers.total++;
                    this.statistics.replicationControllers.replicas += _.get(instance, 'spec.replicas', 0);
                    break;

                case 'Pod':
                    if (_.isUndefined(this.statistics.pods)) {
                        this.statistics.pods = {
                            total: 0,
                            containers: {
                                total: 0,
                                containerTypes: new Set()
                            }

                        };
                    }
                    this.statistics.pods.total++;
                    this.statistics.pods.containers = _.chain(instance).get('spec.containers', []).reduce((result, container) => {
                        result.total++;
                        result.containerTypes.add(container.image);
                        return result;
                    }, this.statistics.pods.containers).value();
                    break;

                default:
                    break;
            }
        });
    }
}

export default DashboardController;
