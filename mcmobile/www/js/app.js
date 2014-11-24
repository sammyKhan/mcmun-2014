// Ionic Starter App
window.app = angular.module('mcmun', ['ionic', 'mcmun.controllers', 'mcmun.services'])

.run(function($ionicPlatform) {
  $ionicPlatform.ready(function() {
    // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
    // for form inputs)
    if(window.cordova && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
    }
    if(window.StatusBar) {
      // org.apache.cordova.statusbar required
      StatusBar.styleDefault();
    }
  });
})


.config(function($stateProvider, $urlRouterProvider, $sceProvider) {

  $sceProvider.enabled(false);

  // Ionic uses AngularUI Router which uses the concept of states
  // Learn more here: https://github.com/angular-ui/ui-router
  // Set up the various states which the app can be in.
  // Each state's controller can be found in controllers.js
  $stateProvider

    .state('delegates', {
       url: '/delegates?committeeId',
       templateUrl: 'templates/delegates.html',
       controller: 'DelegateCtrl'
    })

    .state('forum', {
      url: '/forum?committeeId',
      templateUrl: 'templates/messages.html',
      controller: 'MessagesCtrl'
    })

    .state('me-position', {
      url: '/me/position',
      templateUrl: 'templates/position.html',
      controller: 'PositionCtrl'
    })
    
    .state('menu', {
      url: '/menu',
      templateUrl: 'templates/menu.html',
      controller: 'menuCtrl'
    })

    .state('submenu', {
        url: '/submenu?url&title',
        templateUrl: 'templates/submenu.html',
        controller: 'SubmenuCtrl'
    })

    .state('pdfviewer', {
        url: '/pdfviewer?url&title',
        templateUrl: 'templates/pdfviewer.html',
        controller: 'PDFCtrl'
    })

    .state('browser', {
        url: '/browser?url&title',
        templateUrl: 'templates/browser.html',
        controller: 'BrowserCtrl'
    })
  // if none of the above states are matched, use this as the fallback
  $urlRouterProvider.otherwise('/menu');

});


window.app.apiBaseUrl = '';
