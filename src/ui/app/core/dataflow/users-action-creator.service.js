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

class UsersActionCreatorService {
    constructor(actions, dispatcher, usersAPI, invitesAPI, usersStore) {
        'ngInject';

        this._actions = actions;
        this._dispatcher = dispatcher;
        this._usersAPI = usersAPI;
        this._invitesAPI = invitesAPI;
        this._usersStore = usersStore;

        usersAPI.addOnCreatedListener((user) => this._dispatcher.dispatch({ type: this._actions.USERS_CREATED, user }));
        usersAPI.addOnUpdatedListener((user) => this._dispatcher.dispatch({ type: this._actions.USERS_UPDATED, user }));
        usersAPI.addOnDeletedListener((user) => this._dispatcher.dispatch({ type: this._actions.USERS_DELETED, user }));
    }

    subscribe() {
        this._dispatcher.dispatch({ type: this._actions.USERS_SUBSCRIBE });

        return this._usersAPI.subscribe()
            .then((users) => this._dispatcher.dispatch({ type: this._actions.USERS_SUBSCRIBED, users }));
    }

    update(user) {
        this._dispatcher.dispatch({ type: this._actions.USERS_UPDATE, user });

        return this._usersAPI.update(user)
            .then((updatedUser) => this._dispatcher.dispatch({ type: this._actions.USERS_UPDATED, user: updatedUser }));
    }

    invite(invitations) {
        this._dispatcher.dispatch({ type: this._actions.USERS_INVITE, invitations });

        return this._invitesAPI.create(invitations)
            .then(() => this._dispatcher.dispatch({ type: this._actions.USERS_INVITED }));
    }

    signup(user, code) {
        this._dispatcher.dispatch({ type: this._actions.USERS_SIGN_UP });

        return this._usersAPI.signup(user, code);
    }

    login(user) {
        this._dispatcher.dispatch({ type: this._actions.USERS_LOGIN });

        return this._usersAPI.login(user);
    }

    loggedIn(username) {
        this._dispatcher.dispatch({
            type: this._actions.USERS_LOGGED,
            principal: this._usersStore.get(username)
        });
    }

    logout() {
        return this._$q.when(this._dispatcher.dispatch({ type: this._actions.USERS_LOGOUT }));
    }
}

export default UsersActionCreatorService;
