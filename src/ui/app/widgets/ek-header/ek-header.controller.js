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

class HeaderController {
    constructor($rootScope, $scope, $injector, $state, auth, routerHelper, sessionStore, usersStore) {
        'ngInject';

        const watches = [];
        const onChange = () => {
            this.workspace = this._usersStore.getPrincipal();
            this.sections = getSections(auth, routerHelper);
        };

        this._$injector = $injector;
        this._auth = auth;
        this._$state = $state;
        this._routerHelper = routerHelper;
        this._sessionStore = sessionStore;
        this._usersStore = usersStore;

        this.sections = getSections(auth, routerHelper);
        this.workspace = this._usersStore.getPrincipal();

        this._usersStore.addPrincipalChangeListener(onChange);
        this._selectState();

        watches.concat([
            $rootScope.$on('$stateChangeSuccess', () => this._selectState())
        ]);

        $scope.$on('$destroy', () => {
            this._usersStore.removePrincipalChangeListener(onChange);
            watches.forEach((x) => x());
        });
    }

    _selectState() {
        const currentState = this._$state.current;

        if (currentState.data && currentState.data.header) {
            this.selectedState = _.find(this.sections, (x) => x.data.header.name === currentState.data.header.name);
        }
    }

    goToSection(section) {
        return section.data.header.click(this._$injector);
    }

    isLoggedIn() {
        return this._auth.isLoggedIn();
    }

    logout() {
        this._auth.logout();
    }
}

function getSections(auth, routerHelper) {
    return _.chain(routerHelper.getStates())
        .filter(x => x.data && x.data.header && x.data.header.position && auth.authorize(x.data.access))
        .sort((x, y) => x.data.header.position - y.data.header.position)
        .value();
}

export default HeaderController;
