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

class MetricsActionCreatorService {

    constructor($q, actions, dispatcher, metricsAPI) {
        'ngInject';

        this._$q = $q;
        this._actions = actions;
        this._metricsAPI = metricsAPI;
        this._dispatcher = dispatcher;
    }

    subscribe(namespace) {
        this._dispatcher.dispatch({ type: this._actions.METRICS_SUBSCRIBE});

        return this._metricsAPI.subscribe({ name: namespace.name, kind: 'Namespace' })
            .then((metrics) => this._dispatcher.dispatch({ type: this._actions.METRICS_SUBSCRIBED, metrics }));
    }

    unsubscribe(namespace) {
        this._dispatcher.dispatch({ type: this._actions.METRICS_UNSUBSCRIBE });

        return this._metricsAPI.unsubscribe({ name: namespace.name, kind: 'Namespace' })
            .then(() => this._dispatcher.dispatch({ type: this._actions.METRICS_UNSUBSCRIBED }));
    }
}

export default MetricsActionCreatorService;
