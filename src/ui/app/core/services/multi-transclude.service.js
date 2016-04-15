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

class MultiTranscludeService {
    transclude($element, $transcludeFn) {
        $transcludeFn((clone) => _.chain(clone)
            .filter(x => x.nodeType === 1)
            .each((cloneEl) => {
                const destinationId = getAttribute(cloneEl, 'transclude-to');
                const append = getAttribute(cloneEl, 'transclude-append') === 'true';
                const destination = $element.find(`[transclude-id="${destinationId}"]`);

                if (destination.length) {
                    if (append) {
                        destination.append(cloneEl);
                    } else {
                        destination.html(cloneEl);
                    }
                } else {
                    cloneEl.remove();
                }
            })
            .value());
    }
}

function getAttribute(item, attributeName) {
    const attribute = item.attributes[attributeName];
    let value;

    if (angular.isDefined(attribute)) {
        value = attribute.value;
    }

    return value;
}

export default MultiTranscludeService;
