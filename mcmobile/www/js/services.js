angular.module('mcmun.services', [])

/**
 * A simple example service that returns some data.
 */

.factory('UserService', function($resource) {
  // Might use a resource here that returns a JSON array

  var User = $resource( window.app.apiBaseUrl + '/users', {});
  var Me = $resource( window.app.apiBaseUrl + '/assign', {},{'get':    {method:'GET'},
    'update':   {method:'PUT'}});
  var CommUser = $resource( window.app.apiBaseUrl + '/delegates/:commId', {commId: '@_id'});
  var RoleUser = $resource( window.app.apiBaseUrl + '/roles/:roles', {roles: '@roles'});

  return {
    all: function() {
      var users = User.query();
      return users;
    },
    update: function(committeeId, position, cb) {
      var me = Me.get(function(res) {
        res.committee = committeeId;
        res.position = position;
        console.log(res);
        res.$update(function(data){
          cb(data);
          return data;
        });
      });
    },
    committee: function(cid) {
      var users = CommUser.query({commId: cid});
      return users;
    },
    roles: function(r) {
      var users = RoleUser.query({roles: r});
      return users;
    }
  }
})

.factory('CommitteeService', function($resource, $http) {
  var Committees = $resource( window.app.apiBaseUrl + '/committees', {}, {'query':  {method:'GET', isArray:true}});
  var Committee = $resource( window.app.apiBaseUrl + '/committees/:id', {id: '@_id'},{'get':    {method:'GET'},
    'update':   {method:'PUT'}});

  return {
    all: function() {
      var committees = Committees.query();
      return committees;
    },
    addMessage: function(committeeId, message, cb){
      console.log(committeeId);
      var c = Committee.get({id: committeeId}, function(committee){
        console.log(committee);
        committee.messages.push(message);
        committee.$update(function(data){
          cb(data);
          return data;
        });
      });
    },
    refreshItem: function(committeeId, cb){
      var committee = Committee.get({id: committeeId}, function(data){
        cb(data);
        return data;
      });
    }
  }
})

.factory('AuthService', [
    '$http', 'SessionService',
 
    function($http, SessionService) {
      var AuthService = {
        
        login: function(callback) {
          $http({ method: 'GET', url: window.app.apiBaseUrl + '/users/me' })
          
          // User Successfully Authenticates
          .success(function(data, status, headers, config) {
            SessionService.authenticated = true;
            SessionService.user = data;
            if (typeof(callback) === typeof(Function)) callback();
          })
          
          // Not logged in
          .error(function(data, status, headers, config) {
            console.log('Error authenticating');
            SessionService.authenticated = false; 
            if (typeof(callback) === typeof(Function)) callback();
          });    
        }
      };
 
      return AuthService;
    }
  ])
  .factory('SessionService', function() {
    return {
      user: null,
      authenticated: false
    };
  });
