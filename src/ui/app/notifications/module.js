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

import notificationsRoutes from './notifications-routes';

import NotificationsActionCreator from './notifications-action-creator.service';

import HeaderNotificationsDirective from './ek-header-notifications/ek-header-notifications.directive';
import NotificationsFiltersDirective from './ek-notifications-filters/ek-notifications-filters.directive';
import NotificationListDirective from './ek-notifications-list/ek-notifications-list.directive';
import NotificationsNamespaceSelectorDirective from './ek-notifications-namespace-selector/ek-notifications-namespace-selector.directive';
import NotificationsPreviewDirective from './ek-notifications-preview/ek-notifications-preview.directive';
import NotificationsDirective from './ek-notifications/ek-notifications.directive';
import NotificationsSetupDirective from './ek-notifications-setup/ek-notifications-setup.directive';

const moduleName = 'app.notifications';

angular
    .module(moduleName, [
        coreModule,
        layoutModule,
        widgetsModule
    ])
    .config(notificationsRoutes)

    .service('notificationsNavigationActionCreator', NotificationsActionCreator)

    .directive('ekHeaderNotifications', () => new HeaderNotificationsDirective())
    .directive('ekNotificationsFilters', () => new NotificationsFiltersDirective())
    .directive('ekNotificationsList', () => new NotificationListDirective())
    .directive('ekNotificationsNamespaceSelector', () => new NotificationsNamespaceSelectorDirective())
    .directive('ekNotificationsPreview', () => new NotificationsPreviewDirective())
    .directive('ekNotifications', () => new NotificationsDirective())
    .directive('ekNotificationsSetup', () => new NotificationsSetupDirective());

export default moduleName;
