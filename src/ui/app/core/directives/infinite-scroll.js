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

import Directive from 'directive';

class InfiniteScrollDirective extends Directive {
    constructor() {
        super();

        this.scope = false;
        this.restrict = 'A';
    }

    link($scope, $element, $attrs) {
        const offset = parseInt($attrs.threshold, 10) || 0;
        const element = $element[0];

        $element.bind('mousewheel', () => {
            if (element.scrollTop + element.offsetHeight >= element.scrollHeight - offset) {
                $scope.$evalAsync($attrs.ekInfiniteScroll);
            }
        });
    }
}

export default InfiniteScrollDirective;
