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

import 'angular';

import coreModule from 'core/module';
import layoutModule from 'layout/module';
import widgetsModule from 'widgets/module';

import adminModule from 'admin/module';
import chartsModule from 'charts/module';
import dashboardModule from 'dashboard/module';
import instancesModule from 'instances/module';
import loginModule from 'login/module';

import baseRoutes from './config/base-routes';
import animateConfig from './config/animate-config';
import eventsConfig from './config/events-config';
import logConfig from './config/log-config';
import routerConfig from './config/router-config';
import themeConfig from './config/theme-config';
import authConfig from './config/auth-run';
import dataFlowInitialization from './config/data-flow-initialization-run';

angular
    .module('app', [

        /* Shared modules */
        coreModule,
        layoutModule,
        widgetsModule,

        /* Feature areas */
        adminModule,
        chartsModule,
        dashboardModule,
        instancesModule,
        loginModule
    ])

    .config(animateConfig)
    .config(baseRoutes)
    .config(eventsConfig)
    .config(logConfig)
    .config(routerConfig)
    .config(themeConfig)

    .run(authConfig)
    .run(dataFlowInitialization);

/* eslint no-undef: 0 */
if (PRODUCTION) {
    require('./config/production-config');
}
