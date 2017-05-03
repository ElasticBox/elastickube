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

class NotificationsFiltersController {
    constructor($scope) {
        'ngInject';

        this.selectedNamespace = 'all';
        this.filteredNotifications = [];

        $scope.$watch('ctrl.selectedNamespace', () => this.filterNotificationsByNamespace());
        $scope.$watchCollection('ctrl.notificationsToFilter', () => this.filterNotificationsByNamespace());
    }

    filterNotificationsByNamespace() {
        this.filteredNotifications = _.chain(this.notificationsToFilter)
            .filter((x) => this.selectedNamespace === 'All' || this.selectedNamespace.toLowerCase() === (x.namespace || '').toLowerCase())
            .value();
    }
}

export default NotificationsFiltersController;
