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

import { EventEmitter } from 'events';

const types = {
    INFO: 'INFO',
    WARN: 'WARN',
    ERROR: 'ERROR'
};
const MESSAGE_LIFETIME = 5000;
const CHANGE_EVENT = 'change';

class MessagesService extends EventEmitter {
    constructor() {
        super();

        this._messages = [];
    }

    _addMessage(logMessage) {
        this._messages = this._messages.concat(logMessage);
        this.emit(CHANGE_EVENT);
    }

    _removeMessage(logMessage) {
        this._messages = _.reject(this._messages, (x) => x.id === logMessage.id);
        this.emit(CHANGE_EVENT);
    }

    _removeLater(logMessage) {
        setTimeout(() => this._removeMessage(logMessage), MESSAGE_LIFETIME);
    }

    getMessages() {
        return angular.copy(this._messages);
    }

    removeMessage(logMessage) {
        this._removeMessage(logMessage);
    }

    info(text) {
        const logMessage = {
            id: _.uniqueId(),
            text: text.message || text,
            type: types.INFO
        };

        this._addMessage(logMessage);
        this._removeLater(logMessage);
    }

    warn(text) {
        const logMessage = {
            id: _.uniqueId(),
            text: text.message || text,
            type: types.WARN
        };

        this._addMessage(logMessage);
        this._removeLater(logMessage);
    }

    error(text) {
        this._addMessage({ id: _.uniqueId(), text: text.message || text, type: types.ERROR });
    }

    addChangeListener(callback) {
        this.on(CHANGE_EVENT, callback);
    }

    removeChangeListener(callback) {
        this.removeListener(CHANGE_EVENT, callback);
    }
}

export { MessagesService, types as messageTypes };
