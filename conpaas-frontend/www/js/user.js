/*
 * Copyright (C) 2010-2011 Contrail consortium.                                                                                                                       
 *
 * This file is part of ConPaaS, an integrated runtime environment                                                                                                    
 * for elastic cloud applications.                                                                                                                                    
 *                                                                                                                                                                    
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by                                                                                               
 * the Free Software Foundation, either version 3 of the License, or                                                                                                  
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of                                                                                                     
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                                                                                                      
 * GNU General Public License for more details.                                                                                                                       
 *
 * You should have received a copy of the GNU General Public License                                                                                                  
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

function updateUserCredit() {
	$.ajax({
		url: 'ajax/getCredit.php',
		dataType: 'json',
		success: function(response) {
			if ($('#user_credit').html() != response.credit) {
				$('#user_credit').html(response.credit);
				$('#user_credit_container').css('color', 'red');
				setTimeout("$('#user_credit_container').css('color', '');", 10000);
			}
		}
	});
}

$(document).ready(function() {
	$('#logout').click(function() {
		$.ajax({
			url : 'ajax/login.php',
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
