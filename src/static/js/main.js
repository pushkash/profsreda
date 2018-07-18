(function($) {
	"use strict"
	
	// Preloader
	$(window).on('load', function() {
		$("#preloader").delay(600).fadeOut();
	});

	// Mobile Toggle Btn
	$('.navbar-toggle').on('click',function(){
		$('#header').toggleClass('nav-collapse')
	});

	let BASEURL = window.location.origin+window.location.pathname;

	let url = `${BASEURL}questionnaire/get_questionnaire/1`;
	console.log(url)

	function loadJSON(callback) {   

		var xobj = new XMLHttpRequest();
			xobj.overrideMimeType("application/json");
		xobj.open('GET', url, true); // Replace 'my_data' with the path to your file
		xobj.onreadystatechange = function () {
			  if (xobj.readyState == 4 && xobj.status == "200") {
				// Required use of an anonymous callback as .open will NOT return a value but simply returns undefined in asynchronous mode
				callback(xobj.responseText);
			  }
		};
		xobj.send(null);  
	 }

	 function init() {
		loadJSON(function(response) {
			
		 // Parse JSON string into object
		   var actual_JSON = JSON.parse(response);
		   console.log(actual_JSON)
		});
	   }

	init();

	

	
})(jQuery);