function updateUserCredit() {
	$.ajax({
		url: 'services/getCredit.php',
		dataType: 'json',
		success: function(response) {
			if ($('#user_credit').html() != response.credit) {
				$('#user_credit').html(response.credit);
				$('#user_credit_container').css('color', 'red');
				setTimeout("$('#user_credit_container').css('color', '');", 10000);
			}
			if ($('#user_instances').html() != response.instances) {
				$('#user_instances').html(response.instances);
				$('#user_instances_container').css('color', 'red');
				setTimeout("$('#user_instances_container').css('color', '');", 10000);
			}
		}
	});
}

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
	setInterval('updateUserCredit()', 30000);
});
