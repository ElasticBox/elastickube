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

class AdminChartsController {
    constructor($scope, chartsStore) {
        'ngInject';

        const onChange = () => this.charts = chartsStore.getAll();

        chartsStore.addChangeListener(onChange);

        this.bulkActions = 'Bulk Actions';
        this.charts = chartsStore.getAll();
        this.filteredCharts = [];

        this.tableOptions = {
            data: 'ctrl.filteredCharts',
            enableSelection: false,
            getIdentity: (item) => item._id.$oid,
            columnDefs: [
                {
                    name: 'name',
                    field: 'name',
                    cellTemplate: `<ek-chart-name chart="item"></ek-chart-name>`
                },
                {
                    name: 'maintainers',
                    field: 'maintainers',
                    cellTemplate: `<div>{{ item.maintainers && item.maintainers[0] }}</div>`,
                    sortingAlgorithm: (a, b) => {
                        const sizeA = _.first(a.maintainers);
                        const sizeB = _.first(b.maintainers);

                        if (sizeA > sizeB) {
                            return 1;
                        } else if (sizeA < sizeB) {
                            return -1;
                        }

                        return 0;
                    }
                },
                {
                    name: 'modified',
                    field: 'committed_date',
                    cellTemplate: `<div>{{ item.committed_date | ekHumanizeDate: 'epoch' }} ago</div>`
                }
            ]
        };

        $scope.$on('$destroy', () => chartsStore.removeChangeListener(onChange));
    }
}

export default AdminChartsController;
