
/* Copyright (C) 2010-2013 by Contrail Consortium. */


conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.MysqlPage
     */
    this_module.MysqlPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
    },
    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.getStopWarningText
     */
    getStopWarningText: function () {
        return 'All data stored in the MySQL service ' +
               'will be lost. Are you sure you want to stop the service?';
    },
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        $('#resetPassword').click(this, this.onResetPassword);
        $('#showResetPasswd, #warningResetPasswd').click(function () {
            $('#passwordForm').show();
            $('#resetPasswordForm').show();
            $('#passwd').focus();
        });
        $('.command').click(function () {
            $(this).focus().select();
        });
        $('#dbfile').change(function () {
            $('#loadfile').removeAttr('disabled');
        });
        $('#loadfile').click(function () {
            $('#loadform .loading').show();
            $('#loadform .positive').hide();
            $('#loadform .error').hide();
            $('#loadform').submit();
        });
        $('#loadform').ajaxForm({
            dataType: 'json',
            success: function (response) {
                if (response.error) {
                    that.onLoadFileError(response.error);
                    return;
                }
                $('#loadform .loading').hide();
                $('#loadfile').attr('disabled', 'disabled');
                $('#dbfile').val('');
                $('#loadform .positive').show();
            },
            error: function (response) {
                that.onLoadFileError(response);
            }
        });
    },
    onLoadFileError: function (error) {
        $('#loadform .loading').hide();
        $('#loadform .error').html('Error: <b>' + error + '</b>').show();        
    },
    showResetStatus: function (type, message) {
        var otherType = (type === 'positive') ? 'error' : 'positive';
        $('#resetStatus').removeClass(otherType).addClass(type)
            .html(message)
            .show();
        setTimeout(function () {
            $('#resetStatus').fadeOut();
        }, 3000);
    },
    // handlers
    onResetPassword: function (event) {
        var page = event.data,
            passwd = $('#passwd').val(),
            passwdRe = $('#passwdRe').val(),
            user = $('#user').html();

        if (passwd.length < 8) {
            page.showResetStatus('error', 'Password too short');
            $('#passwd').focus();
            return;
        }
        if (passwd !== passwdRe) {
            page.showResetStatus('error', 'Retyped password does not match');
            $('#passwdRe').focus();
            return;
        }
        // send the request
        $('#resetPassword').attr('disabled', 'disabled');
        page.server.req('ajax/setPassword.php', {
            sid: page.service.sid,
            user: user,
            password: passwd
        }, 'post', function (response) {
            // successful
            page.showResetStatus('positive', 'Password was reset successfuly');
            $('#resetPassword').removeAttr('disabled');
            $('#passwd').val('');
            $('#passwdRe').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showResetStatus('error', 'Password was not reset');
            $('#resetPassword').removeAttr('disabled');
        });
    }
    });
    
    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var service,
        page,
        sid = GET_PARAMS['sid'],
        server = new conpaas.http.Xhr();
    server.req('ajax/getService.php', {sid: sid}, 'get', function (data) {
        service = new conpaas.model.Service(data.sid, data.state,
                data.instanceRoles, data.reachable);
        page = new conpaas.ui.MysqlPage(server, service);
        page.attachHandlers();
        if (page.service.needsPolling()) {
            page.freezeInput(true);
            page.pollState(function () {
                window.location.reload();
            });
        }
    }, function () {
        // error
        window.location = 'services.php';
    })
});

	google.load("visualization", "1", {packages:["corechart"]});
	coords=[
          ['time', 'Misalignment' ],
          ['10s',  0      ],
	  ['9s',  0      ],
          ['8s',  0 ],
          ['7s',  0],
	  ['6s',  0],
  	  ['5s',  0],
          ['4s',  0],
	  ['3s',  0],
	  ['2s',  0],
	  ['1s',  0],
	  ['0s', 0]
          ];
var sid = getUrlVars()["sid"];
      function drawChart() {

	//update table data
	for (i=1;i<coords.length-1;i++)
		coords[i][1]=coords[i+1][1];
	
	$.get("ajax/galeraPerformance.php?sid="+sid,function(data){coords[coords.length-1][1]=parseFloat(data);$('#ordinaryLoad').html(coords[coords.length-1][1].toFixed(2));});
        var data = google.visualization.arrayToDataTable(coords);
        var options = {
          title: 'Galera Mean Misalignment'
        };
        var chart = new google.visualization.LineChart(document.getElementById('chart_div'));
        chart.draw(data, options);
      }
	 


if($(".chart_div")){
window.setInterval(drawChart, 1000);
google.setOnLoadCallback(drawChart);
}

        //inizialization of the stats var       
        var stats= new Array(10);
	var statsPS= new Array(10);
        stats[0]=['10s', 'Select%', 'Update%','Insert%','Delete%'];
        for ( var i =1; i<10;i++){
           stats[i]=[''+10-i+'s',0,0,0,0];
	   statsPS[i]=[''+10-i+'s',0,0,0,0];
        }

    function drawStats() {
        //chart time shifting
        for ( var i =1; i<9;i++){
           for (var j=1; j<stats[i].length;j++){
			stats[i][j]=stats[i+1][j];
	   		statsPS[i][j]=statsPS[i+1][j];
	    }
       }
// get the last update usage data from the cluster
        $.ajax({ type: "GET", 
                 url: "ajax/getGaleraStats.php?sid="+sid,  
                success: function (data) {
                         var parsed= JSON.parse(data);
                      
                        statsPS[stats.length-1]=[ '0s', 
                                                parsed['result']['meanSelect'] ,
                                                parsed['result']['meanUpdate'] ,
                                                parsed['result']['meanInsert'],
                                                parsed['result']['meanDelete'] ];

			stats[stats.length-1]=[ '0s',
                                                statsPS[statsPS.length-1][1]-statsPS[statsPS.length-2][1] ,
						statsPS[statsPS.length-1][2]-statsPS[statsPS.length-2][2] ,
						statsPS[statsPS.length-1][3]-statsPS[statsPS.length-2][3] ,
						statsPS[statsPS.length-1][4]-statsPS[statsPS.length-2][4] 
                                               ];

		var tot_operation= (+stats[stats.length-1][1]
                                    +stats[stats.length-1][2]
                                    +stats[stats.length-1][3]
                                    +stats[stats.length-1][4]
				    )/100; //normalization to get in percentage
		stats[stats.length-1]=[ '0s',
                                                stats[stats.length-1][1]/ tot_operation ,
                                                stats[stats.length-1][2]/ tot_operation ,
                                                stats[stats.length-1][3]/ tot_operation ,
                                                stats[stats.length-1][4]/ tot_operation ];	

                 }, 
               error: function () { console.log("Error"); }}
);

        var data = google.visualization.arrayToDataTable(stats);
        var options = {
          title: 'Cluster Usage',
          hAxis: {title: 'Time in Sec',  titleTextStyle: {color: '#333'}},
          vAxis: {minValue: 0 , maxValue:100 }
        };
        var chart = new google.visualization.AreaChart(document.getElementById('stats_div'));
        chart.draw(data, options);
      }
if ($("#stats_div")){
window.setInterval(drawStats, 1000);
google.setOnLoadCallback(drawStats);
}

if ($("#stats_div")){
window.setInterval(gangliaMonitor, 5000);
google.setOnLoadCallback(gangliaMonitor);
}



var nodesStats = Array();
function gangliaMonitor(){
nodesStats = Array();
$.ajax({ type: "GET",
                 url: "ajax/getGaleraGangliaParams.php?sid="+sid,
                success: function (data) {
                        var parsed= JSON.parse(data);
			var xml = parsed['result']['Ganglia'][1];	
			xmlDoc=$.parseXML(xml);
			var $xml = $( xmlDoc );
  			$xml.find( "GRID" ).find("CLUSTER").find("HOST").each(function(){
											var host= new Object;
											if ($(this).attr("IP") =="127.0.0.1" || $(this).attr("NAME") =="conpaas")
												host["hostname"]="Manager";
											else 
												 host["hostname"]=$(this).attr("IP");
														

											$(this).find('METRIC[NAME="cpu_idle"]').each(function (){
											host[$(this).attr("NAME")]=$(this).attr("VAL");
												});


											$(this).find('METRIC[NAME="disk_free"]').each(function (){
                                                                                        host[$(this).attr("NAME")]=$(this).attr("VAL");
                                                                                                });
									

											$(this).find('METRIC[NAME="disk_total"]').each(function (){
                                                                                        host[$(this).attr("NAME")]=$(this).attr("VAL");
                                                                                                });

                                                                                        $(this).find('METRIC[NAME="mem_free"]').each(function (){
                                                                                        host[$(this).attr("NAME")]=$(this).attr("VAL");        
											});

											$(this).find('METRIC[NAME="mem_total"]').each(function (){
                                                                                        host[$(this).attr("NAME")]=$(this).attr("VAL");
                                                                                        });


                                                                                        $(this).find('METRIC[NAME="pkts_in"]').each(function (){
                                                                                                host[$(this).attr("NAME")]=$(this).attr("VAL");});
														
                                                                                        $(this).find('METRIC[NAME="pkts_out"]').each(function (){
                                                                                        host[$(this).attr("NAME")]=$(this).attr("VAL");
                                                                                                });


                                                                                        $(this).find('METRIC[NAME="bytes_out"]').each(function (){
											host[$(this).attr("NAME")]=$(this).attr("VAL");
                                                                                                });


                                                                                        $(this).find('METRIC[NAME="bytes_in"]').each(function (){
                                                                                               host[$(this).attr("NAME")]=$(this).attr("VAL"); });
										nodesStats.push(host);
										}
									 );
	 
	var found=false;
	var i=0;
	while (!found  && i<nodesStats.length){
		if(nodesStats[i]["hostname"]=="Manager"){
			var app=nodesStats[0];
			nodesStats[0]=nodesStats[i];
			nodesStats[i]=app;
			found=true;
	}
	i++;
	}
	stampa(nodesStats);
	}});

}

  



function stampa(z){
        var MAXDISKUSAGE=0.85, MAXCPUUSAGE=85, MAXMEMUSAGE=0.75;

	var addresses = document.getElementsByClassName('address');
	var hosts=new Array(addresses.length);
	for (var i=0 ; i<addresses.length;i++)
        	hosts[i]=addresses[i].innerText;
	
	var table = document.getElementById('tableID');
        var tbody = table.getElementsByTagName('tbody')[0];
       
	while(tbody.firstChild) {
    tbody.removeChild(tbody.firstChild);
}

        for (index = 0; index < z.length; index++) {
		if (hosts.indexOf(z[index]["hostname"])!=-1  || z[index]["hostname"]=="Manager"){
     			 var newtr = document.createElement('tr');
		       	 tbody.appendChild(newtr);
        		 var newtd = document.createElement('td');
		         var tx = document.createTextNode(z[index]["hostname"]);


		        newtd.appendChild(tx);
        		newtr.appendChild(newtd);

        		var td = document.createElement('td');
			var cpuUsage=(100-z[index]["cpu_idle"]).toFixed(2);
		        var tx = document.createTextNode(cpuUsage+" %");
		        td.appendChild(tx);
			if (cpuUsage >MAXCPUUSAGE){
        			td.style.fontWeight = 'bold';
				td.style.color="red";
				td.style.borderColor="red";
				td.style.borderWidth="3px";
				td.style.borderStyle = "solid";
			}

			newtr.appendChild(td);

        		var td = document.createElement('td');
        		var tx = document.createTextNode((z[index]["mem_free"]/1024).toFixed(2)+" MB");
        		td.appendChild(tx);
			var memUsage=1-z[index]["mem_free"]/z[index]["mem_total"];
			if (memUsage >MAXMEMUSAGE){
                		td.style.fontWeight = 'bold';
		                td.style.color="red";
                		td.style.borderColor="red";
                		td.style.borderWidth="3px";
		                td.style.borderStyle = "solid";
       			 }		
        		newtr.appendChild(td);
	
			var td = document.createElement('td');
		        var tx = document.createTextNode((parseFloat(z[index]["disk_free"])).toFixed(2)+" GB");
		        var diskUsage=1-z[index]["disk_free"]/z[index]["disk_total"];
			td.appendChild(tx);
		 	if (diskUsage >MAXDISKUSAGE){
        			td.style.fontWeight = 'bold';
		      		td.style.color="red";
	        		td.style.borderColor="red";
			        td.style.borderWidth="3px";
			        td.style.borderStyle = "solid";
       			 }

		        newtr.appendChild(td);

			var td = document.createElement('td');
		        var tx = document.createTextNode(z[index]["pkts_in"]);
		        td.appendChild(tx);
		        newtr.appendChild(td);

			var td = document.createElement('td');
		        var tx = document.createTextNode(z[index]["pkts_out"]);
		        td.appendChild(tx);
		        newtr.appendChild(td);

		        var td = document.createElement('td');
		        var tx = document.createTextNode((z[index]["bytes_in"]/1024).toFixed(2));
		        td.appendChild(tx);
		        newtr.appendChild(td);

			var td = document.createElement('td');
		        var tx = document.createTextNode((z[index]["bytes_out"]/1024).toFixed(2));
		        td.appendChild(tx);
		        newtr.appendChild(td);
			var td = document.createElement('td');
		        newtr.appendChild(td);
		//	if (cpuUsage>MAXCPUUSAGE || memUsage>MAXMEMUSAGE || diskUsage>MAXDISKUSAGE )
		//	newtr.style.backgroundColor="#fb4b4b";

			if (z[index]["hostname"]!="Manager"){
        				var a = document.createElement('input');
		        		a.setAttribute("class","elimina");
				        a.setAttribute("value","Delete");
				        a.setAttribute("type","button");
					a.setAttribute("id",z[index]['hostname']);
					a.setAttribute("name",sid);
					a.style.backgroundColor="#28597a";
					a.style.borderWidth="0px";
					a.style.color="#ffffff";
					a.style.padding="5px";
		        		a.onclick= function(){
        						var permission = confirm('Are you sure you want to delete the node:'+this.id+' ?');
							var link="ajax/galeraRemoveSpecific.php?sid="+sid+"&ip="+this.id;
			        			if(permission) {
	 							location.href = link;                  
		        				}       
        						else {          
								return;
        						}       
						};

					td.appendChild(a);
			}

			}
   		}
		
   }

	
function getUrlVars() {
    var vars = {};
    var parts = window.location.href.replace(/[?&]+([^=&]+)=([^&]*)/gi, function(m,key,value) {
        vars[key] = value;
    });
    return vars;
}
