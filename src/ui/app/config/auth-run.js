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

function checkRouteAccess($rootScope, auth, initialization, instancesNavigationActionCreator, loginNavigationActionCreator, routerHelper,
    sessionStore) {
    'ngInject';

    $rootScope.$on('$stateChangeStart', (event, toState, toParams, fromState) => {
        if (initialization.initialized) {
            if (!auth.authorize(toState.data.access)) {
                event.preventDefault();

                if (fromState.url === '^') {
                    if (auth.isLoggedIn()) {
                        instancesNavigationActionCreator.instances();
                    } else {
                        sessionStore.setInitialState(toState.name, toParams);
                        loginNavigationActionCreator.login();
                    }
                }
            }
        } else {
            event.preventDefault();

            initialization.deferred.promise.then(() => {
                routerHelper.changeToState(toState, toParams);
            });
        }
    });
}

export default checkRouteAccess;
