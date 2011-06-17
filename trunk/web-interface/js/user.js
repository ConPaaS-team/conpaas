$(document).ready(function() {
	$('#logout').click(function() {
		$.ajax({
			url : 'services/login.php',
			data : {
				action : 'logout'
			},
			dataType : 'json',
			type : 'post',
			success : function(response) {
				if (typeof response.error != 'undefined') {
					alert('Error: ' + response.error);
				} else if (response.logout == 1) {
					window.location = 'login.php';
				}
			}
		});
	});
});
