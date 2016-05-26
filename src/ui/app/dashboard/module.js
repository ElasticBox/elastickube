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

import coreModule from 'core/module';
import layoutModule from 'layout/module';
import widgetsModule from 'widgets/module';

import dashboardRoutes from './dashboard-routes';

import NavigationActionCreator from './navigation-action-creator.service';

import DashboardDirective from './ek-dashboard/ek-dashboard.directive';
import DashboardBarDirective from './ek-dashboard-bar/ek-dashboard-bar.directive';
import DashboardCardDirective from './ek-dashboard-card/ek-dashboard-card.directive';
import DashboardLineChartDirective from './ek-dashboard-linechart/ek-dashboard-linechart.directive';

const moduleName = 'app.dashboard';

angular
    .module(moduleName, [
        coreModule,
        layoutModule,
        widgetsModule
    ])
    .config(dashboardRoutes)

    .service('dashboardNavigationActionCreator', NavigationActionCreator)

    .directive('ekDashboard', () => new DashboardDirective())
    .directive('ekDashboardBar', () => new DashboardBarDirective())
    .directive('ekDashboardCard', () => new DashboardCardDirective())
    .directive('ekDashboardLinechart', () => new DashboardLineChartDirective());

export default moduleName;
