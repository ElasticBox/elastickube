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

import profiles from 'core/security/profiles';

const states = [{
    state: 'admin',
    config: {
        abstract: true,
        parent: 'private',
        template: '<ek-admin flex></ek-admin>',
        url: '/admin',
        controller: ($scope, settingsActionCreator) => {
            'ngInject';

            $scope.$on('$destroy', () => settingsActionCreator.unsubscribe());
        },
        data: {
            access: profiles.ADMIN
        },
        resolve: {
            loading: (settingsActionCreator) => {
                'ngInject';

                return settingsActionCreator.subscribe();
            }
        }
    }
}, {
    state: 'admin.settings',
    config: {
        template: '<ek-admin-settings></ek-admin-settings>',
        url: '/settings',

        /* eslint no-undefined: 0 */
        params: {
            focusSection: undefined
        },
        data: {
            header: {
                name: 'admin',
                position: 4,
                click: ($injector) => {
                    const actionCreator = $injector.get('adminNavigationActionCreator');

                    return actionCreator.settings();
                }
            }
        }
    }
}, {
    state: 'admin.users',
    config: {
        template: '<ek-admin-users></ek-admin-users>',
        url: '/users',
        data: {
            header: {
                name: 'admin'
            }
        }
    }
}, {
    state: 'admin.namespaces',
    config: {
        template: '<ek-admin-namespaces></ek-admin-namespaces>',
        url: '/namespaces',
        data: {
            header: {
                name: 'admin'
            }
        }
    }
}, {
    state: 'admin.charts',
    config: {
        template: '<ek-admin-templates></ek-admin-templates>',
        url: '/charts',
        data: {
            header: {
                name: 'admin'
            }
        }
    }
}, {
    state: 'admin.instances',
    config: {
        template: '<ek-admin-instances></ek-admin-instances>',
        url: '/instances',
        data: {
            header: {
                name: 'admin'
            }
        },
        resolve: {
            loading: ($q, instancesActionCreator, namespacesStore) => {
                'ngInject';

                return $q.all(_.map(namespacesStore.getAll(), (x) => instancesActionCreator.subscribe(x)));
            }
        }
    }
}];

function adminRoutes(routerHelperProvider) {
    'ngInject';

    routerHelperProvider.configureStates(states);
}

export default adminRoutes;
