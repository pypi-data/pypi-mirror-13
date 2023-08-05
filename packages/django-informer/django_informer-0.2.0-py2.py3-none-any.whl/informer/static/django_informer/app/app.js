(function () {
    'use strict';

    var app = angular.module('informer', [
        'ngRoute',
        'ngResource',
        'ngAria',
        'ngAnimate',
        'ngMaterial',
        'informer.settings',
        'informer.home',
        'informer.checker'
    ]);

    // default filters
    app.filter('name', function() {
        return function(input) {
            input = input || '';

            var patterns = ['Informer', 'informer-']

            angular.forEach(patterns, function (pattern) {
                input = input.replace(pattern, '').toLowerCase();
            })

            return input
        };
    });

    // default routes
    app.config(['$routeProvider', function ($routeProvider) {
        // dashboard
        $routeProvider.when('/dashboard', {
            templateUrl: '/static/django_informer/app/home/dashboard.tmpl.html',
            controller: 'DashboardController'
        });

        // detail
        $routeProvider.when('/detail/:informer', {
            templateUrl: '/static/django_informer/app/checker/detail.tmpl.html',
            controller: 'DetailController'
        });

        $routeProvider.otherwise({
            redirectTo: '/dashboard'
        });
    }]);

    // base url is defined on template

    /*app.constant('CONFIGURATION', {
        'URL': '/informer/'
    });*/

    // default configurations
    app.config(function ($mdThemingProvider) {
        $mdThemingProvider.theme('default')
            .primaryPalette('blue')
            .accentPalette('indigo');
    });

})();
