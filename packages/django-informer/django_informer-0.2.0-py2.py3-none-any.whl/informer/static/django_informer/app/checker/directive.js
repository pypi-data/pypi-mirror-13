(function () {
    'use strict';

    var checker = angular.module('informer.checker');

    checker.directive('informerTimeSeriesChart', ['MeasureService', 'CONFIGURATION', function (Measure, Configuration) {
        return {
            restrict: 'A',
            template: '',
            scope: {
                informer: '@',
                measure: '@'
            },
            link: function (scope, element, attrs) {
                google.charts.setOnLoadCallback(drawChart);

                function drawChart () {
                    var data = new google.visualization.DataTable(),
                        chart = new google.charts.Line(element[0]),
                        params = {
                            'informer': scope.informer,
                            'measure': scope.measure
                        };

                    data.addColumn('datetime', null);
                    data.addColumn('number', scope.measure);

                    Measure.get(params, function (response) {
                        response.result.map(function (item) {
                            var date = new Date(item.date),
                                value = parseFloat(item.value);

                            data.addRow([date, value]);
                        });

                        chart.draw(data, {
                            chart: {
                                title: scope.measure,
                                subtitle: 'data collected by ' + scope.informer + ' to ' + scope.measure
                            }
                        });
                    });
                }

                function onFailure () {
                }
            }
        };
    }]);

})();
