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

const TRANSITION_DURATION = 500;

class DashboardLineChartController {

    constructor($element, $location, $scope) {
        'ngInject';

        this._$element = $element;
        this._$location = $location;

        this.initialized = false;
        this._timeFormat = d3.time.format('%Y-%m-%dT%H:%M:%SZ').parse;

        $scope.$watch('ctrl.dataset', (dataset) => {
            if (!_.isUndefined(dataset)) {
                if (!this.initialized) {
                    $scope.$evalAsync(() => this._updateChart());
                    this.initialized = !this.initialized;
                } else if (this.dataset.length > 0) {
                    this._tick();
                }
            }
        });
    }

    _tick() {
        this._dates = [];
        this._values = [];
        this.dataset.forEach((d) => {
            this._dates.push(this._timeFormat(d.timestamp));
            this._values.push(_.get(d, this.datafield));
        });
        this._xScale.domain(d3.extent(this._dates));

        const yExtent = d3.extent(this._values);
        const yRange = yExtent[1] - yExtent[0];

        yExtent[0] -= yRange * 0.1;
        yExtent[1] += yRange * 0.1;

        this._yScale.domain(yExtent);

        this._yAxis.transition()
            .duration(TRANSITION_DURATION)
            .ease('linear')
            .call(this._yScale.axis);

        this._xAxis.transition()
            .duration(TRANSITION_DURATION)
            .ease('linear')
            .call(this._xScale.axis);

        this._path.attr('d', this._pathGenerator(this._dates));
    }

    _updateChart() {
        const container = this._$element.find('.ek-dashboard-linechart__container__svg');
        const chartWidth = container.width();
        const chartHeight = container.height();
        const margin = { top: 5, right: 25, bottom: 20, left: 35 };

        this.svg = d3.select(container[0]).append('svg')
            .attr('width', chartWidth - margin.right)
            .attr('height', chartHeight);

        this.svg.append('defs')
            .append('svg:clipPath')
            .attr('id', 'clip')
            .append('svg:rect')
            .attr('id', 'clip-rect')
            .attr({
                x: margin.left,
                y: margin.top,
                width: chartWidth - margin.right - margin.left,
                height: chartHeight - margin.top - margin.bottom
            });

        const axes = this.svg.append('g')
            .attr('pointer-events', 'none')
            .attr('class', 'ek-dashboard-linechart__container__svg__axes')
            .style('font-size', '11px');

        const chart = this.svg.append('g')
            .attr('class', 'ek-dashboard-linechart__container__svg__plot-area')
            .attr('pointer-events', 'none')
            .attr('clip-path', `url(${this._$location.url()}#clip)`);

        const backRect = this.svg.append('rect')
            .style('stroke', 'none')
            .style('fill', '#FFF')
            .style('fill-opacity', 0)
            .attr({
                x: margin.left,
                y: margin.top,
                width: chartWidth - margin.right - margin.left,
                height: chartHeight - margin.top - margin.bottom,
                'pointer-events': 'all'
            });

        this._dates = [];
        this._values = [];

        this.dataset.forEach((d) => {
            this._dates.push(this._timeFormat(d.timestamp));
            this._values.push(_.get(d, this.datafield));
        });

        this._xScale = d3.time.scale()
            .range([margin.left, chartWidth - margin.right])
            .domain(d3.extent(this._dates));

        const yExtent = d3.extent(this._values);
        const yRange = yExtent[1] - yExtent[0];

        yExtent[0] -= yRange * 0.1;
        yExtent[1] += yRange * 0.1;

        this._yScale = d3.scale.linear()
            .range([chartHeight - margin.bottom, margin.top])
            .domain(yExtent);

        this._xAxis = axes.append('g')
            .attr('class', 'ek-dashboard-linechart__container__svg__axes__x')
            .attr('transform', `translate(0, ${(chartHeight - margin.bottom)})`)
            .call(this._xScale.axis = d3.svg.axis()
                .orient('bottom')
                .outerTickSize(0)
                .ticks(5)
                .innerTickSize(0)
                .scale(this._xScale));

        this._yAxis = axes.append('g')
            .attr('class', 'ek-dashboard-linechart__container__svg__axes__y')
            .attr('transform', `translate(${margin.left}, 0 )`)
            .call(this._yScale.axis = d3.svg.axis()
                .orient('left')
                .outerTickSize(0)
                .ticks(5)
                .innerTickSize(-(chartWidth - margin.left - margin.right))
                .scale(this._yScale));

        this._yScale(d3.mean(this._values));

        this._pathGenerator = d3.svg.line()
            .interpolate('basis')
            .x((d, i) => this._xScale(this._dates[i]))
            .y((d, i) => this._yScale(this._values[i]));

        this._series = chart.append('g');

        this._path = this._series.append('path')
            .attr('vector-effect', 'non-scaling-stroke')
            .style('stroke', this.lineColor)
            .attr('d', this._pathGenerator(this._dates));

        const zoom = d3.behavior.zoom()
            .scaleExtent([1, 12])
            .x(this._xScale)
            .on('zoom', () => {
                this._xAxis.call(this._xScale.axis);

                this._series.attr('transform', `translate(${d3.event.translate[0]}, 0) scale(${d3.event.scale}, 1)`);
            });

        backRect.call(zoom);
    }
}

export default DashboardLineChartController;
