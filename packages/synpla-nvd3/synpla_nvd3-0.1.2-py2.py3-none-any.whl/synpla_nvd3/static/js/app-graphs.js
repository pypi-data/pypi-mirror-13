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
