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

import AbstractStore from './abstract-store';

const CHANGE_EVENT = 'change';
const MAX_RECORDS = 500;

class MetricsStoreService extends AbstractStore {
    constructor(session, actions, dispatcher) {
        'ngInject';

        super(session);

        this._actions = actions;

        this.dispatchToken = dispatcher.register((action) => {
            switch (action.type) {
                case this._actions.METRICS_SUBSCRIBED:
                    this.metrics = action.metrics;
                    this.emit(CHANGE_EVENT);
                    break;

                case this._actions.METRIC_CREATED:
                    this._addMetric(action.metric);
                    this.emit(CHANGE_EVENT);
                    break;

                default:
            }
        });
    }

    _addMetric(metric) {
        this.metrics.unshift(metric);
        if (this.metrics.length > MAX_RECORDS) {
            this.metrics.pop();
        }
        this.metrics = _.sortBy(this.metrics, 'timestamp').reverse();
    }

    getMetrics() {
        return this.metrics || [];
    }

    addChangeListener(callback) {
        this.on(CHANGE_EVENT, callback);
    }

    removeChangeListener(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
}

export default MetricsStoreService;
