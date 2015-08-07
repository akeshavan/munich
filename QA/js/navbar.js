angular.module('aknavbar', [])

.controller('aknavbarCtrl', ['$scope', '$window', '$http', '$sce',
  function($scope, $window, $http, $sce) {
	  //$scope.columns = $scope.data.names
	  //$scope.values = $scope.data.vals
	  console.log("loadedNavbar")
	  }
	  
])

.directive('aknavbar', function() {
  return {
    templateUrl: "templates/navbar.html",
    restrict: 'EC',
    replace: true,
    controller: 'aknavbarCtrl',
    scope: {info: '=ngModel'},
    link: function(scope, element, attrs) {
     //do stuff 
	
    }
  };
});