// app for SendOut, AngularJS

app.factory('pdfs', function($http){
    var myService = {
        getter: function(system){
            return $http.get('/qm_list/' + system.toLowerCase());
        }
    }
    return myService;
});

app.factory('pdfdl', function($http){
    var myService = {
        download: function(sys, file){
            return $http.get('/qm_download/', 
            				{
            					params: {system: sys, filename: file},
            					responseType: 'blob'
            				});
        }
    }
    return myService;
});

app.controller('myCtrl', function(pdfs, pdfdl, $scope, $sce, $location){
	var tmp = $location.absUrl().split('/');
	$scope.dataLoaded = false;
	$scope.system = tmp[tmp.length - 1];
	$scope.pdfLoading = false;
	var dataStream = pdfs.getter($scope.system);
	dataStream.then(
		function(result){
			$scope.data = result.data;
			$scope.dataLoaded = true;
		},
		function(result){
			console.log($scope.data);
		}
	);

	$scope.pdfDownload = function(sys, file){
		$scope.pdfLoading = true;
		pdfdl.download(sys, file).then(
			function(result){
				var file = new Blob([result.data], {type: result.headers("content-type")});
				var fileURL = URL.createObjectURL(file);
				$scope.pdf_content = $sce.trustAsResourceUrl(fileURL);
			}, 
			function(result){
				console.log('letoltes sikertelen')
			});
		$scope.pdfLoading = false;
	}
});