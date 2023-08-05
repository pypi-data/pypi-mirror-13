(function () {
    'use strict';

    var checker = angular.module('informer.checker');

    checker.factory('DiscoverService', ['$resource', 'CONFIGURATION', DiscoverService]);
    checker.factory('InformerService', ['$resource', 'CONFIGURATION', InformerService]);
    checker.factory('MeasureService', ['$resource', 'CONFIGURATION', MeasureService]);

    function DiscoverService ($resource, Configuration) {
        return $resource(
            Configuration.URL + 'discover/',
            {},
            {
                'query': { method: 'GET' }
            }
        );
    }

    function InformerService ($resource, Configuration) {
        return $resource(
            Configuration.URL + ':informer/',
            {'informer': '@informer'},
            {
                'get': { method: 'GET' }
            }
        );
    }

    function MeasureService ($resource, Configuration) {
        return $resource(
            Configuration.URL + ':informer/:measure/',
            {'informer': '@informer', 'measure': '@measure'}
        );
    }

})();
