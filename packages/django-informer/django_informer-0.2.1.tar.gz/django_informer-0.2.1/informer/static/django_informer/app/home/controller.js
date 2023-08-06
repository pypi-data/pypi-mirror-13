(function () {
    'use strict';

    var home = angular.module('informer.home', ['ngResource']);

    home.controller('DashboardController', ['$scope', 'DiscoverService', 'InformerService', DashboardController]);

    function DashboardController ($scope, Discover, Informer) {
        $scope.informers = [];
        $scope.message = 'All systems operational.';

        var informers = Discover.query({}, successOnGetInformersList, fail);

        function successOnGetInformersList (response) {
            angular.forEach(response.result, function (item) {
                Informer.get(
                    { 'informer': item.name },
                    successOnGetInformerDetails,
                    failureOnGetInformerDetails);
            });
        }

        function successOnGetInformerDetails (response) {
            if (!response.operational) {
                $scope.message = 'Oh my god. Something goes wrong.';
            }

            $scope.informers.push(response);
        }

        function failureOnGetInformerDetails (response) {
            $scope.message = 'Some problems were found.';
        }

        function fail () {
            $scope.message = 'Crap. A error ocurred.';
        }
    }

})();
