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

class AdminEditNamespaceController {
    constructor($scope, usersStore, namespacesActionCreator) {
        'ngInject';

        this._namespacesActionCreator = namespacesActionCreator;

        this.labels = _.get(this.namespace, 'metadata.labels') || {};
        this.namespaceName = _.get(this.namespace, 'metadata.name');
        this.users = this.namespace ? _.map(this.namespace.members, (username) => usersStore.get(username))
            : [usersStore.getPrincipal()];

        $scope.$watchGroup(['ctrl.form.$valid', 'ctrl.users'], ([isValid, users]) => {
            this.dialogController.canAccept = isValid && _.size(users) > 0;
        });
    }

    countLabels() {
        return _.size(this.labels);
    }

    removeUser(user) {
        this.users = _.without(this.users, user);
    }

    setLabels() {
        return (labels) => this.labels = labels;
    }

    accept() {
        const namespaceInfo = {
            namespaceName: this.namespaceName,
            labels: this.labels,
            users: this.users
        };

        if (this.namespace) {
            return this._namespacesActionCreator.updateNamespace(this.namespace, this.users);
        }
        return this._namespacesActionCreator.createNamespace(namespaceInfo);
    }
}

export default AdminEditNamespaceController;
