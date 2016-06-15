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

function instancesRoutes(routerHelperProvider) {
    'ngInject';

    routerHelperProvider.configureStates([{
        state: 'instances',
        config: {
            url: '/:namespace/instances',
            parent: 'private',
            template: '<ek-instances flex></ek-instances>',
            controller: (checkNamespace) => {
                'ngInject';

                checkNamespace.execute();
            },
            data: {
                header: {
                    name: 'instances',
                    position: 2,
                    click: ($injector) => {
                        const actionCreator = $injector.get('instancesNavigationActionCreator');

                        return actionCreator.instances();
                    }
                }
            },
            resolve: {
                loading: ($q, instancesStore, namespacesStore) => {
                    'ngInject';

                    return $q.all([instancesStore.isLoading(), namespacesStore.isLoading()]);
                }
            }
        }
    }, {
        state: 'instance',
        config: {
            abstract: true,
            url: '/:namespace/instances/{instanceId:[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}}',
            parent: 'private',
            template: '<ek-instance flex></ek-instance>',
            onExit: ($stateParams, checkNamespace, instanceActionCreator, instancesStore) => {
                'ngInject';

                const namespace = $stateParams.namespace;
                const instanceId = $stateParams.instanceId;

                checkNamespace.execute();

                const instance = _.find(instancesStore.getAll(),
                    (x) => _.matchesProperty('metadata.namespace', namespace)(x) && _.matchesProperty('metadata.uid', instanceId)(x));

                instanceActionCreator.unsubscribe(instance);
            },
            data: {
                header: {
                    name: 'instances'
                }
            },
            resolve: {
                loading: ($q, $stateParams, instanceActionCreator, instancesStore, namespacesStore) => {
                    'ngInject';

                    return $q.all([instancesStore.isLoading(), namespacesStore.isLoading()])
                        .then(() => {
                            const instance = instancesStore.get($stateParams.instanceId);

                            return instanceActionCreator.subscribe(instance);
                        });
                }
            }
        }
    }, {
        state: 'instance.overview',
        config: {
            url: '/',
            template: '<ek-instance-overview></ek-instance-overview>'
        }
    }, {
        state: 'instance.events',
        config: {
            url: '/events',
            template: '<ek-instance-events-block></ek-instance-events-block>',
            resolve: {
                checkInstanceType: ($q, $stateParams, instancesNavigationActionCreator, instancesStore) => {
                    'ngInject';

                    return instancesStore.isLoading()
                        .then(() => {
                            const instance = instancesStore.get($stateParams.instanceId);

                            if (instance.kind !== 'Pod') {
                                return instancesNavigationActionCreator.instance($stateParams, { location: 'replace' });
                            }

                            return $q.when();
                        });
                }
            }
        }
    }, {
        state: 'instance.containers',
        config: {
            url: '/containers',
            template: '<ek-instance-containers></ek-instance-containers>',
            resolve: {
                checkInstanceType: ($q, $stateParams, instancesNavigationActionCreator, instancesStore) => {
                    'ngInject';

                    return instancesStore.isLoading()
                        .then(() => {
                            const instance = instancesStore.get($stateParams.instanceId);

                            if (instance.kind !== 'Pod') {
                                return instancesNavigationActionCreator.instance($stateParams, { location: 'replace' });
                            }

                            return $q.when();
                        });
                }
            }
        }
    }, {
        state: 'new-instance',
        config: {
            url: '/instances/new',

            /* eslint no-undefined: 0 */
            params: {
                chart: undefined
            },
            parent: 'private',
            template: '<ek-new-instance flex></ek-new-instance>',
            data: {
                header: {
                    name: 'instances'
                }
            }
        }
    }]);
}

export default instancesRoutes;
