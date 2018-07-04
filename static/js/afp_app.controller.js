// app for SendOut, AngularJS

app.factory('afps', function($http){
    var myService = {
        getter: function(system){
            return $http.get('/afps/' + system);
        }
    }
    return myService;
});

app.factory('download', function($http){
    var myService = {
        actual: function(system, filename){
        	console.log(system, filename);
            return $http.post('/afps/' + system, {'filename': filename});
        }
    }
    return myService;
});

app.controller('myCtrl', function(afps, download, $scope, $location){
	$scope.dataLoaded = false;
	var tmp = $location.absUrl().split('/');
	$scope.system = tmp[tmp.length - 1];
	var dataStream = afps.getter($scope.system);
	dataStream.then(
		function(result){
			$scope.dataLoaded = true;
			$scope.data = result.data;
		},
		function(result){
			console.log($scope.data);
		}
	);

	$scope.download = function(sys, file){
		var dl = download.actual(sys, file);
		reader = new FileReader();
		dl.then(
			function(data, status, headers, config, statusText){
				console.log(data);
				var blob = new Blob([data], {type: 'application/zip'});
				reader.readAsDataURL(blob);
			}, 
			function(result){
				console.log('something went wrong');
			});
		reader.onload = function(e){
			window.open(decodeURIComponent(reader.result), '_self', '', false);
		}
	};
});