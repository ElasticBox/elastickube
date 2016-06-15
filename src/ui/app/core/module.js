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

import './core.less';

import 'angular-aria';
import 'angular-animate';
import 'angular-cookies';
import 'angular-messages';
import 'angular-material/angular-material';

import apiModule from 'blocks/api/module';
import routerModule from 'blocks/router/module';

import actions from './dataflow/actions';
import ChartsActionCreatorService from './dataflow/charts-action-creator.service.js';
import ChartsStoreService from './dataflow/charts-store.service.js';
import DispatcherService from './dataflow/dispatcher.service.js';
import InstanceActionCreatorService from './dataflow/instance-action-creator.service.js';
import InstanceStoreService from './dataflow/instance-store.service.js';
import InstancesActionCreatorService from './dataflow/instances-action-creator.service.js';
import InstancesStoreService from './dataflow/instances-store.service.js';
import LogActionCreatorService from './dataflow/log-action-creator.service.js';
import LogStoreService from './dataflow/log-store.service.js';
import MetricsActionCreatorService from './dataflow/metrics-action-creator.service.js';
import MetricsStoreService from './dataflow/metrics-store.service.js';
import NamespacesActionCreatorService from './dataflow/namespaces-action-creator.service.js';
import NamespacesStoreService from './dataflow/namespaces-store.service.js';
import NotificationsActionCreatorService from './dataflow/notifications-action-creator.service';
import NotificationsStoreService from './dataflow/notifications-store.service.js';
import SessionActionCreatorService from './dataflow/session-action-creator.service';
import SessionStoreService from './dataflow/session-store.service.js';
import SettingsActionCreatorService from './dataflow/settings-action-creator.service';
import SettingsStoreService from './dataflow/settings-store.service';
import UsersActionCreatorService from './dataflow/users-action-creator.service';
import UsersStoreService from './dataflow/users-store.service.js';

import humanizeDateFilter from './filters/humanize-date.filter';

import FocusDirective from './directives/focus';
import InfiniteScrollDirective from './directives/infinite-scroll';

import AuthService from './security/auth.service';
import CheckNamespaceService from './services/check-namespace.service';
import InitializationService from './services/initialization.service';
import MultiTranscludeService from './services/multi-transclude.service';
import { MessagesService } from './services/messages.service.js';
import SessionService from './services/session.service';

const moduleName = 'app.core';

angular
    .module(moduleName, [
        'ngMaterial',
        'ngAnimate',
        'ngCookies',
        'ngMessages',
        'ngSanitize',
        apiModule,
        routerModule
    ])

    .constant('storage', localStorage)
    .constant('actions', actions)

    .filter('ekHumanizeDate', () => humanizeDateFilter)

    .service('auth', AuthService)
    .service('checkNamespace', CheckNamespaceService)
    .service('dispatcher', DispatcherService)
    .service('initialization', InitializationService)
    .service('multiTransclude', MultiTranscludeService)
    .service('messages', MessagesService)
    .service('session', SessionService)

    .service('chartsActionCreator', ChartsActionCreatorService)
    .service('chartsStore', ChartsStoreService)

    .service('instanceActionCreator', InstanceActionCreatorService)
    .service('instanceStore', InstanceStoreService)

    .service('instancesActionCreator', InstancesActionCreatorService)
    .service('instancesStore', InstancesStoreService)

    .service('logActionCreator', LogActionCreatorService)
    .service('logStore', LogStoreService)

    .service('metricsActionCreator', MetricsActionCreatorService)
    .service('metricsStore', MetricsStoreService)

    .service('namespacesActionCreator', NamespacesActionCreatorService)
    .service('namespacesStore', NamespacesStoreService)

    .service('notificationsActionCreator', NotificationsActionCreatorService)
    .service('notificationsStore', NotificationsStoreService)

    .service('sessionActionCreator', SessionActionCreatorService)
    .service('sessionStore', SessionStoreService)

    .service('settingsActionCreator', SettingsActionCreatorService)
    .service('settingsStore', SettingsStoreService)

    .service('usersActionCreator', UsersActionCreatorService)
    .service('usersStore', UsersStoreService)

    .directive('ekFocus', () => new FocusDirective())
    .directive('ekInfiniteScroll', () => new InfiniteScrollDirective());

export default moduleName;
