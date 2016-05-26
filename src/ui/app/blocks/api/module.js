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

import ChartsAPIService from './charts-api.service';
import InstanceAPIService from './instance-api.service';
import InstancesAPIService from './instances-api.service';
import LogsAPIService from './logs-api.service';
import MetricsAPIService from './metrics-api.service';
import NamespacesAPIService from './namespaces-api.service';
import PrincipalAPIService from './principal-api.service';
import SettingsAPIService from './settings-api.service';
import UsersAPIService from './users-api.service';
import InvitesAPIService from './invites-api.service';
import WebsocketClientService from './websocket-client.service';

const moduleName = 'blocks.api';

angular
    .module(moduleName, [])

    .service('chartsAPI', ChartsAPIService)
    .service('instanceAPI', InstanceAPIService)
    .service('instancesAPI', InstancesAPIService)
    .service('logsAPI', LogsAPIService)
    .service('metricsAPI', MetricsAPIService)
    .service('namespacesAPI', NamespacesAPIService)
    .service('principalAPI', PrincipalAPIService)
    .service('settingsAPI', SettingsAPIService)
    .service('usersAPI', UsersAPIService)
    .service('invitesAPI', InvitesAPIService)

    .service('websocketClient', WebsocketClientService);

export default moduleName;
