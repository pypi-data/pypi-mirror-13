/*global jQuery */

(function(window, $) {
  'use strict';

  $(function() {
    var barChartNonTimeSeries = function(data, metricTitle, graphElement, graphColours) {
      var chart = nv.models.multiBarChart();

      var margin = {top: 10, right: 80, bottom: 150, left: 60},
          height = ($(window).height() - 500) > 500 ? ($(window).height() - 500) : 500,
          width = parseInt($(graphElement).css('width').replace('px', ''));

      if (navigator.userAgent.indexOf('PhantomJS') !== -1) {
        width *= $(graphElement).parent().parent().hasClass('col-sm-12') ? 1.5 : 0.7;
      }

      chart.margin(margin)
           .height(height)
           .width(width);

      chart.x(function(d) {
          return d.title;
        });

      chart.y(function(d) {
          return d.value;
        });

      chart.yAxis.tickFormat(d3.format(','));

      chart.tooltips(true)
           .duration(350);

      if (typeof data.isGrouped === 'undefined') {
        chart.stacked(true);
      }

      if (graphColours) {
        chart.color(graphColours);
      }

      var dataMap = {};
      var newData = [];
      var el = null;

      for (var i = 0; i < data.filtered.length; i++) {
        el = data.filtered[i];

        if (typeof el.dimension === 'undefined' || !el.dimension) {
          el.dimension = metricTitle;
        }

        if (!(el.dimension in dataMap)) {
          dataMap[el.dimension] = [];
        }

        dataMap[el.dimension].push({
          'title': el.title,
          'value': el.value
        });
      }

      $.each(dataMap, function(k, v) {
        newData.push({'key': k, 'values': v});
      });

      var svg = d3.select(graphElement).append("svg");

      svg.datum(newData)
          .transition()
          .duration(500)
          .call(chart)
          .style({'height': height + 'px', 'width': width + 'px'});

      // Line up x-axis labels to be centred on each bar / line in the chart.
      // Thanks to:
      // http://stackoverflow.com/a/13472375/2066849
      var xTicks = svg.select('.nv-x.nv-axis > g').selectAll('g');
      xTicks
          .selectAll('text')
          .attr('transform', function(d,i,j) {return 'translate (-12, 70)  rotate(-90 0,0)';});

      nv.utils.windowResize(chart.update);

      return chart;
    };

    var linePlusBarChart = function(data, metricTitle, graphElement, graphColours) {
      var chart = nv.models.discreteBarChart();

      var margin = {top: 30, right: 70, bottom: 150, left: 70},
          height = ($(window).height() - 500) > 500 ? ($(window).height() - 500) : 500,
          width = parseInt($(graphElement).css('width').replace('px', ''));

      if (navigator.userAgent.indexOf('PhantomJS') !== -1) {
        width *= $(graphElement).parent().parent().hasClass('col-sm-12') ? 1.5 : 0.7;
      }

      var xdomain = {};
      data[0].values.forEach(function(d) {
        xdomain[d[1]] = d[0];
      });

      chart.margin(margin)
           .height(height)
           .width(width);

      chart.x(function(d,i) { return d[1] })
           .y(function(d,i) { return d[2] });

      chart.color(['steelblue']);

      chart.xAxis
          .tickFormat(function(d){ return xdomain[d]; })
          .rotateLabels(-45)
          .axisLabel("Completed Iterations");

      chart.yAxis
          .tickFormat(d3.format(','))
          .axisLabel("Change Per Iteration");

      var svg = d3.select(graphElement).append("svg");

      svg.datum([data[0]])
         .transition()
         .duration(0)
         .call(chart)
         .style({'height': height + 'px', 'width': width + 'px'});

      svg.select('.nv-y.nv-axis').select('.nv-wrap').select('g')
        .append('rect')
        .attr('width', 10)
        .attr('height', 10)
        .attr('x', -60)
        .attr('y', (height-margin.top-margin.bottom)/2 + 60)
        .attr('stroke', 'steelblue')
        .attr('fill', 'steelblue');

      svg.select('.nv-x.nv-axis').select('.nv-wrap').select('text.nv-axislabel').attr('x', function(d){
        return (width-margin.left-margin.right) / 2;
      });

      /** line chart **/
      if (data[0].values.length > 1) {

          var x = d3.scale.ordinal()
              .rangeBands([0, width-margin.right-margin.left], .1);

          var y = d3.scale.linear()
              .range([height - margin.bottom - margin.top, 0]);

          var yAxis = d3.svg.axis()
              .scale(y)
              .orient("right")
              .ticks(5);

          var line = d3.svg.line()
              .x(function(d) { return x(d[1]) + x.rangeBand() / 2; })
              .y(function(d) { return y(d[2]); });

          x.domain(data[1].values.map(function(d){return d[1]; }));
          y.domain([0, d3.max(data[1].values, function(d) { return d[2]; })]);

          var linechart = svg.append('g')
             .attr('class','custom-line-wrap')
             .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

          linechart.append("g")
            .attr("class", "y axis")
            .attr("transform", "translate(" + (width - margin.left - margin.right) + " ,0)")
            .call(yAxis)
          .append("text")
            .attr("transform", "rotate(90)")
            .attr("x", (height-margin.top-margin.bottom)/2)
            .attr("y", -50)
            .style("text-anchor", "middle")
            .style("font-size", "12px")
            .text("Cumulative Change");

          svg.select('.custom-line-wrap').select('.y.axis')
            .append('circle')
            .attr('r', 3)
            .attr('cx', 52)
            .attr('cy', (height-margin.top-margin.bottom)/2 - 60)
            .attr('stroke', 'red')
            .attr('fill', 'red');

          var tooltip = nv.models.tooltip();
          //tooltip.duration(0);

          linechart.selectAll('.dot')
            .data(data[1].values)
            .enter().append('circle')
              .attr("class", 'dot')
              .attr('cx', function(d) { return x(d[1]) + x.rangeBand() / 2;  })
              .attr('cy', function(d) { return y(d[2]); })
              .attr('stroke', 'red')
              .attr('fill', 'red')
              .attr('r', 3);/*
              .on('mouseover', function(d,i) {
                var data = {series: {
                    key: 'Cumulative Charge',
                    value: d[1],
                    color: "red"
                }};
                tooltip.data(data).hidden(false);
              })
              .on('mouseout', function(d,i) {
                  tooltip.hidden(true);
              })
              .on('mousemove', function(d,i) {
                  tooltip.position({top: d3.event.pageY, left: d3.event.pageX})();
              });*/

          linechart.append("path")
            .datum(data[1].values)
            .attr("class", "line")
            .attr("d", line)
            .style('fill', 'none')
            .style('stroke', 'red')
            .style('stroke-width', '1.5px');

      }

      nv.utils.windowResize(chart.update);

      return chart;

    };

    var pieChart = function(data, metricTitle, graphElement, graphColours) {
      var extraHeight = 0;

      var width = parseInt($(graphElement).css('width').replace('px', '')),
          margin = {top: 0, right: 20, bottom: 20, left: 30},
          height = width > 500 ? (navigator.userAgent.indexOf('PhantomJS') !== -1 ? (300 + extraHeight) : (500 + extraHeight)) : width * 1.1;

      if (navigator.userAgent.indexOf('PhantomJS') !== -1) {
        width *= 0.7;
      }

      var chart = nv.models.pieChart()
          .x(function(d) {
            return d.title;
          })
          .y(function(d) {
            return d.value;
          })
          .margin(margin)
          .height(height)
          .width(width)
          .valueFormat(d3.format(','))
          .showLabels(true)
          .labelType('value')
          .labelThreshold(0)
          .showLegend(true)
          .donut(true)
          .donutRatio(0.3);

      if (graphColours) {
        chart.color(graphColours);
      }

      var svg = d3.select(graphElement).append("svg");

      svg.datum(data.filtered)
          .transition()
          .duration(500)
          .call(chart)
          .style({'height': height + 'px', 'width': width + 'px'});

      nv.utils.windowResize(chart.update);

      return chart;
    };

    var draw = function(data, graphWrapperElement, metricTitle, displayMode) {
      $(graphWrapperElement).append('<section class="graph"></section>');

      var graphElement = graphWrapperElement + ' > .graph';
      var graphColours = null;

      data['isPrint'] = navigator.userAgent.indexOf('PhantomJS') !== -1;

      switch (displayMode) {
        case 'bar-chart-non-time-series':
          nv.addGraph(function() {
            barChartNonTimeSeries(data, metricTitle, graphElement, graphColours);
          });
          return;

        case 'line-plus-bar-chart':
          nv.addGraph(function() {
            linePlusBarChart(data, metricTitle, graphElement, graphColours);
          });
          return;

        case 'pie-chart':
          nv.addGraph(function() {
            pieChart(data, metricTitle, graphElement, graphColours);
          });
          return;
      }
    };

    if (typeof graphData !== 'undefined' && graphData.length) {
      $.each(graphData, function(i, gd) {
        draw(gd.data,
             gd.graphWrapperElement,
             gd.metricTitle,
             gd.displayMode);
      });
    }
  });
})(window, jQuery);
