// app for SendOut, AngularJS

app.factory('zips', function($http){
    var myService = {
        getter: function(system){
            return $http.get('/zips/' + system);
        }
    }
    return myService;
});

app.factory('send', function($http){
    var myService = {
        file: function(system, filename){
            return $http.post('/zips/' + system, {'filename': filename});
        }
    }
    return myService;
});

app.controller('myCtrl', function(zips, send, $scope, $location){
	var tmp = $location.absUrl().split('/');
	$scope.system = tmp[tmp.length - 1];
	var dataStream = zips.getter($scope.system);
	dataStream.then(
		function(result){
			$scope.data = result.data;
		},
		function(result){
			console.log($scope.data);
		}
	);

	$scope.sendOut = function(sys, file){
		var sendOut = send.file(sys, file);
		sendOut.then(
			function(result){
				console.log('sent successfully');
			}, 
			function(result){
				console.log('something went wrong');
			});
	};
});