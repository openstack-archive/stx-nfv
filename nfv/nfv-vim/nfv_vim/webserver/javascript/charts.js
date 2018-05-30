/*
 * Copyright (c) 2017 Wind River Systems, Inc.
*
* SPDX-License-Identifier: Apache-2.0
*
 */

var Chart = function(element, options) {
    var self = this;
    var title = options.title;
    var margin = options.margin;
    var series = options.series;
    var x_axis_ticks = options.x_axis_ticks;
    var y_axis_ticks = options.y_axis_ticks;
    var line_chart_width = options.width - margin.left - margin.right;
    var line_chart_height = options.height - margin.top - margin.bottom;

    //self.drag_move = function(d) {
    //    console.log(d3.event.dx);
    //};
    //
    //var drag = d3.behavior.drag()
    //    .origin(function(d) { return d; })
    //    .on("dragstart", self.drag_move)
    //    .on("drag", self.drag_move)
    //    .on("dragend", self.drag_move);

    var x = d3.time.scale().range([0, line_chart_width]);
    var y = d3.scale.linear().range([line_chart_height, 10]);

    var xAxis = d3.svg.axis().scale(x)
        .orient("bottom").ticks(x_axis_ticks);
        //.tickFormat(formatTime);

    var yAxis = d3.svg.axis().scale(y)
        .orient("left").ticks(y_axis_ticks).tickFormat(d3.format("d"))
        .tickSubdivide(0);

    var valueLine = d3.svg.line()
        .x(function(d) { return x(d.x); })
        .y(function(d) { return y(d.y); });
        //.interpolate(basis);

    var chart = d3.select(element)
        .style("border", "1px solid #ddd")
        .style("padding", "5px")
        .append("svg")
            .attr("width", line_chart_width + margin.left + margin.right)
            .attr("height", line_chart_height + margin.top + margin.bottom)
        .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var hover = d3.select(element).append("div")
        .attr("class", "hover")
        .style("opacity", 1);

    self.make_x_axis_grid = function() {
        return d3.svg.axis().scale(x).orient("bottom").ticks(5)
    };

    self.get_hover_content = function(d) {
        var s = series[d.series_id];

        return '<p" style="display: block; color: white;">' + s.label + ': '
               + d.y + '<br>' + d.x.toLocaleString() + '</p>';
    };

    self.zero_data = function () {
        for (var series_i = 0; series_i < series.length; series_i++) {
            for (tick_i=0; tick_i < series[series_i].data.length; tick_i++) {
                series[series_i].data[tick_i].y = 0;
            }
        }
    };

    self.initialize = function() {
        // Initial data for series
//        var now = new Date().getTime();
//        for (var series_i = 0; series_i < series.length; series_i++) {
//            for (tick_i=0; tick_i < x_axis_ticks; tick_i++) {
//                series[series_i].data.unshift(
//                        {series_id: series_i, id: uuid++,
//                         x: (new Date(now - (5000 * tick_i))), y: 0});
//            }
//        }

        // Add Title
        chart.append("text")
            .attr("class", "title")
            .attr("x", 0 - margin.left)
            .attr("y", 0 - (margin.top / 2))
            .text(title);

        // Box around the chart
        chart.append("rect")
            .style("stroke", "#ddd")
            .style("stoke-width", "1px")
            .style("fill", "none")
            .attr("x", 0)
            .attr("y", 0)
            .attr("width", line_chart_width)
            .attr("height", line_chart_height);

        // Add the X Axis Grid Lines
        chart.append("g")
            .attr("class", "grid")
            .attr("transform", "translate(0," + line_chart_height + ")")
            .call(self.make_x_axis_grid()
                .tickSize(-line_chart_height, 0, 0)
                .tickFormat("")
            );

        // Add the X-Axis
        chart.append("g")
            .attr("class", "x_axis")
            .style("font-size", "12px")
            .style("fill", "#bbb")
            .attr("transform", "translate(0," + line_chart_height + ")")
            .call(xAxis);


        // Add the Y-Axis
        chart.append("g")
            .attr("class", "y_axis")
            .style("font-size", "12px")
            .style("fill", "#bbb")
            .call(yAxis);

        // Add value-lines
        for (var series_i = 0; series_i < series.length; series_i++) {
            chart.append("path").attr("id", "line"+series_i)
                .style("stroke", series[series_i].color)
                .attr("d", valueLine(series[series_i].data));
        }

        self.zero_data();
    };

    self.update = function(data) {

        // Add series data.
        for (var series_i = 0; series_i < series.length; series_i++) {
            data[series_i].sort( function(a, b) {
                if (a.x < b.x) return -1;
                if (a.x > b.x) return 1;
                return 0;
            });

            data[series_i].forEach(function(d) {
                d.x = new Date(d.x);
                d.y = +d.y;
            });

            for (var data_i = 0; data_i < data[series_i].length; data_i++) {
                series[series_i].data.unshift(data[series_i][data_i]);
            }
        }

        // Scale the range of the data.
        x.domain(d3.extent(series[0].data, function(d) { return d.x; }));
        y.domain([0, d3.max(series[0].data, function(d) { return d.y; })]);

        // Update axises.
        chart.select("g.x_axis").transition().duration(500).call(xAxis);
        chart.select("g.y_axis").transition().duration(500).call(yAxis);

        chart.select("g.grid").transition().duration(500)
            .call(self.make_x_axis_grid().tickSize(-line_chart_height, 0, 0)
                  .tickFormat(""));

        // Updating lines.
        for (var series_i = series.length-1; series_i >= 0; series_i--) {
            chart.select("#line"+series_i)
                .attr("d",  valueLine(series[series_i].data))
                .transition().duration(500).ease("linear")
                .style("stroke", series[series_i].color);
        }

        // Updating hover dots.
        for (var series_i = 0; series_i < series.length; series_i++) {
            // Update hover dots.
            var dots = chart.selectAll(".dots"+series_i)
                .data(series[series_i].data, function(d) {return d.id; })

            dots.transition()
                .duration(500)
                .attr("cx", function(d) { return x(d.x); })
                .attr("cy", function(d) { return y(d.y); });

            // Add new hover dots.
            dots.enter().append("circle").classed("dots"+series_i, true)
                .style("stroke", series[series_i].color)
                .style("fill", series[series_i].color)
                .style("opacity", 1)
                .attr("r", 2)
                .attr("cx", function(d) { return x(d.x); })
                .attr("cy", function(d) { return y(d.y); })
                .on("mouseover", function(d) {
                    var matrix = this.getScreenCTM()
                         .translate(+this.getAttribute("cx"),
                         +this.getAttribute("cy"));
                    hover.transition()
                        .duration(500)
                        .style("opacity", 1)
                        .style("background-color", series[d.series_id].color)
                    hover.html(self.get_hover_content(d))
                        .style("font-size", "11px")
                        .style("left", (window.pageXOffset + matrix.e + 10)  + "px")
                        .style("top", (window.pageYOffset + matrix.f - 35) + "px")
                })
                .on("mouseout", function(d) {
                    hover.transition()
                        .duration(250)
                        .style("opacity", 0);
                });

            // Delete old hover dots.
            dots.exit()
                .remove();
        }

        // Delete older series data.
        for (var series_i = 0; series_i < series.length; series_i++) {
            for (var data_i = 0; data_i < data[series_i].length; data_i++) {
                if (series[series_i].data.length > x_axis_ticks) {
                    series[series_i].data.pop();
                }
            }
        }
    };

    self.clear = function() {
        self.zero_data();

        // Clear scales.
        x.domain(d3.extent(series[0].data, function(d) { return d.x; }));
        y.domain([0, d3.max(series[0].data, function(d) { return d.y; })]);

        // Update axises.
        chart.select("g.x_axis").transition().duration(500).call(xAxis);
        chart.select("g.y_axis").transition().duration(500).call(yAxis);

        chart.select("g.grid").transition().duration(500)
            .call(self.make_x_axis_grid().tickSize(-line_chart_height, 0, 0)
                  .tickFormat(""));

        // Clear lines.
        for (var series_i = 0; series_i < series.length; series_i++) {
            chart.select("#line"+series_i).remove();
            chart.append("path").attr("id", "line"+series_i)
                .style("stroke", series[series_i].color)
                .attr("d", valueLine(series[series_i].data));
        }
    }
};
