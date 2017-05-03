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

import Drop from 'tether-drop';
import './ek-drop.less';
import Directive from 'directive';
import Controller from './ek-drop.controller';

class DropDirective extends Directive {

    constructor() {
        'ngInject';

        super({ Controller });

        this.bindToController = {
            openOn: '@?',
            beforeClose: '&',
            targetPosition: '@',
            position: '@',
            remove: '@?'
        };
    }

    compile(tElement) {
        tElement.addClass('ek-drop');

        return {
            post: ($scope, $elem, attr, ctrl) => {
                const dropOptions = {
                    target: ctrl.target,
                    content: ctrl.content,
                    constraintToWindow: true,
                    constrainToScrollParent: true,
                    openOn: ctrl.openOn || 'click',
                    position: ctrl.targetPosition || 'bottom left',
                    remove: ctrl.remove === 'true',
                    tetherOptions: {
                        attachment: ctrl.position || 'top right'
                    }
                };

                if (ctrl.beforeClose && _.isFunction(ctrl.beforeClose())) {
                    dropOptions.beforeClose = ctrl.beforeClose();
                }
                ctrl.drop = new Drop(dropOptions);

                $scope.$on('$destroy', () => {
                    ctrl.drop.destroy();
                });
            }
        };
    }
}

export default DropDirective;
