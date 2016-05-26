/*
Copyright 2016 ElasticBox All rights reserved.

Licensed under the Apache License, Version 2.0 (the 'License');
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an 'AS IS' BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

import d3 from 'd3';

class DashboardBarController {

    constructor($element) {
        'ngInject';

        const svgContainer = $element.find('.ek-dashboard-bar__container__svg');
        const width = svgContainer.width();
        const height = svgContainer.height();
        const svg = d3.select(svgContainer[0]).append('svg')
            .attr('width', width)
            .attr('height', height);

        const maxDomain = this.percentage ? 100 : this.max;
        const scale = d3.scale.linear().domain([0, maxDomain]).range([0, width]);
        const bar = svg.selectAll('g')
            .data([this.value])
            .enter().append('g');

        this.unit = this.percentage ? '%' : this.unit;

        bar.append('rect')
            .attr('fill', this.color)
            .attr('height', height)
            .attr('width', (d) => scale(d));

        bar.append('text')
            .attr('x', 10)
            .attr('y', height / 2)
            .attr('dy', '.35em')
            .text(this.title);
    }
}

export default DashboardBarController;

