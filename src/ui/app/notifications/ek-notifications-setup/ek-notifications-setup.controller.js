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

class NotificationsSetupController {
    constructor($scope, usersActionCreator, usersStore) {
        'ngInject';

        const onChange = () => this.principal = angular.copy(this._usersStore.getPrincipal());

        this._usersStore = usersStore;

        this._usersStore.addPrincipalChangeListener(onChange);
        this.principal = angular.copy(this._usersStore.getPrincipal());
        $scope.$on('$destroy', () => this._usersStore.removePrincipalChangeListener(onChange));

        $scope.$watch('ctrl.principal.notifications', (newValue, oldValue) => {
            if (!_.isEqual(newValue, oldValue)) {
                usersActionCreator.update(this.principal);
            }
        }, true);
    }
}

export default NotificationsSetupController;
