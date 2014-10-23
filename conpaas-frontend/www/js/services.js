
/* Copyright (C) 2010-2013 by Contrail Consortium. */



/**
 * interaction for services.php - main dashboard
 * @require conpaas.js
 */
conpaas.ui = (function (this_module) {
    this_module.Dashboard = conpaas.new_constructor(
    /* extends */conpaas.ui.Page,
    /* constructor */function (server, application) {
        this.server = server;
        this.application = application;
        this.jplot = null;
        // this.poller = new conpaas.http.Poller(server, 'ajax/checkServices.php', 'get');
        this.poller = new conpaas.http.Poller(server, 'ajax/getProfilingInfo.php', 'get');
    },
    /* methods */{
    /**
     * @param {Service} service that caused the polling to be continued
     */
    displayInfo_: function (service) {
        var info = 'at least one service is in a transient state';
        if (!service.reachable) {
            info = 'at least one service is unreachable'
        }
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
    },
    displayInfo_2: function (info) {
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
    },
    pollState: function (onStableState, onInstableState, maxInterval) {
        var that = this;
        this.poller.poll(function (response) {
            if(response.ready){
                that.displayInfo_2('Profiling...');
                var profile = response.profile.profile;
                that.updateProfileInfo(profile);
                
                if(response.profile.state == 'RUNNING'){
                    conpaas.ui.visible('pgstatInfo', false);
                    var downlink = '<a class="button small" href="ajax/getProfilingInfo.php?aid='+that.application.aid+'&format=file">Download profile</a><br/>';
                    $("#downloadProfile").html(downlink); 
                    return true;
                }
                // $("#divProfile").html(JSON.stringify(response));
            }else{
                that.displayInfo_2('Starting application manager...');
            }

            if (typeof onInstableState === 'function') {
                onInstableState(response);
            }
            return false;
        }, {aid: this.application.aid}, maxInterval);
    },
    updateProfileInfo: function(profile){
		var str = '<table class="slist" cellpadding="0" cellspacing="0" style="border: 1px solid;">',
		tdclass = 'wrapper ';
		
		str += '<tr style="background:#fffdf6"><th width="30" style="padding:5px">Status</th><th width="255">Configuration</th><th width="50" style="padding:5px">Time(s)</th><th width="50" style="padding:5px">Cost(&euro;)</th></tr>';

		var exps = [];
		var pareto = [];

		for (var i = 0; i < profile.experiments.length; i++) {
			var img = 'running';
			if (i == profile.experiments.length - 1)
				tdclass += 'last';
			str += '<tr class="service">';
			if (profile.experiments[i].Done)
				img='tick';
			str += '<td align="center" class="'+tdclass+'" style="border-left: 1px solid #ddd;"><img src="images/' + img + '.gif"/></td>';
			str += '<td align="center" class="'+tdclass+'">' + this.objToString(profile.experiments[i].Configuration) + '</td>';
			//str += '<td class="'+tdclass+'">' + that.objToString(response.profiling_info[i].Arguments) + '</td>';
			if (profile.experiments[i].Done){
				str += '<td align="center" class="'+tdclass+'">' + profile.experiments[i].Results.ExeTime + '</td>';
				str += '<td align="center" class="'+tdclass+'">' + profile.experiments[i].Results.TotalCost + '</td>';
				exps.push([profile.experiments[i].Results.TotalCost, profile.experiments[i].Results.ExeTime]);
			}else
				str += '<td colspan="2" class="'+tdclass+'">' + '' + '</td>';
			str += '</tr>';

			
		}
		str += '</table>'; 
		
		
		for (var i = 0; i < profile.pareto.length; i++) 
			if(profile.pareto[i].Done)
				pareto.push([profile.pareto[i].Results.TotalCost, profile.pareto[i].Results.ExeTime]);

		if(exps.length > 0 || pareto.length > 0){
			$("#divProfileTable").html(str); 
			this.plot(exps, pareto);
		}
	},
    objToString: function(obj){
        var str = '';
        for (var property in obj) {
            if (obj.hasOwnProperty(property)) {
                str += property + ':' + obj[property] + ', ';
            }
        }
        
        return str.substring(0, str.length - 2).replace(/%/g, '');
    },
    plot: function (experiments, pareto){
        if (this.jplot != null)
        {
            this.jplot.destroy();
            this.jplot.series[0].data = experiments;
            this.jplot.series[1].data = pareto;
            this.jplot.replot({resetAxes:true});

        }else{
            this.jplot = $.jqplot('divProfileChart',  [experiments, pareto],
            { 
            series:[ 
                  {showLine:false, markerOptions: { size: 7, style:"circle" }},
                  {showMarker:false, linePattern: '-.', lineWidth: 2, rendererOptions: {smooth: true} }
                  ],
              seriesColors:['#4990D6', '#3AB5A5'],   
              axes:{
                xaxis:{
                  label:'Cost (euro)',
                  labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                yaxis:{
                  label:'Time (sec)',
                  labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                }
              },
              highlighter: {
                show: true,
                sizeAdjust: 7.5
              },
              cursor:{
				show: true,
				zoom:true,
				showTooltip:false
			  } 
            }

            );
        }
    },

    makeDeleteHandler_: function (service) {
        var that = this;
        return function () {
            that.deleteService(service);
        };
    },
    saveName: function (newName, onSuccess, onError) {
        this.server.req('ajax/renameApplication.php',
                {name: newName}, 'post',
                onSuccess, onError);
    },
    onClickName: function (event) {
        var page = event.data;
        var newname = prompt("Enter a new name", $('#name').html());
        if (!newname) {
            return;
        }
        page.saveName(newname, function () {
            $('#name').html(newname);
        })
    },
    onClickProfile: function (event) {
        var that = event.data; 
        var manfile = $('#manfile')[0].files[0];
        var appfile = $('#appfile')[0].files[0];
        var formData = new FormData();
        formData.append('manfile', manfile, manfile.name);
        formData.append('appfile', appfile, appfile.name);
        $.ajax({
          url: 'ajax/uploadManifest.php',
          data: formData,
          cache: false,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
            // alert(data.appid); 
            that.application =  new conpaas.model.Application(data.appid);
            // alert(that.application.aid);
            that.pollState(function () {
                window.location.reload();
            }, null, 5);
          }
       });
  

    },
    onChangeManifest: function (event) {
		var idspanname = this.id + 'name';
		$( "#"+idspanname).html( $('#'+this.id)[0].files[0].name );
        var file = $('#manfile')[0].files[0];
        var formData = new FormData();
        formData.append('manifest', file, file.name);
        $.ajax({
          url: 'ajax/parseManifest.php',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
            $('#name').html(data.applicatio_name);
            var html = '<div class="services"><table class="slist" cellspacing="1" cellpadding="0">';
            for(var i = 0; i < data.services.length; i++){
             html += '<tr class="service"><td class="colortag colortag-stopped"></td> \
             <td class="wrapper last"> \
               <div class="icon"><img src="images/'+data.services[i].module_type+'.png" height="64"></div> \
               <div class="content" style="padding-left:20px"> \
                  <div class="title">'+data.services[i].module_name+'<img class="led" title="initialized" src="images/ledgray.png"></div> \
                  <div class="actions">Service not initialized</div> \
               </div> \
               <div class="statistic"> \
                  <!--div class="statcontent"><img src="images/throbber-on-white.gif"></div> \
                  <div class="note">loading...</div--> \
               </div> \
               <div class="clear"></div> \
            </td></tr>';
            }
            html += '</table></div>';

            $('#servicesWrapper').html(html);
          }
       });
        
    },
    onUploadProfile: function(event)
    {  
		var that = event.data; 
		//var profile = response.profile.profile;
        //that.updateProfileInfo(profile);
		//var idspanname = this.id + 'name';
		//$( "#"+idspanname).html( $('#'+this.id)[0].files[0].name );
        var file = $('#profilefile')[0].files[0];
        var formData = new FormData();
        formData.append('profile', file, file.name);
        $.ajax({
          url: 'ajax/uploadProfile.php',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
			  that.updateProfileInfo(data);
				//alert(JSON.stringify(data));
          }
       });
	},
	onUploadSLO: function(event)
    {  
		var that = event.data; 
        var file = $('#slofile')[0].files[0];
        var formData = new FormData();
        formData.append('slo', file, file.name);
        $.ajax({
          url: 'ajax/uploadSLO.php',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
			  //$('#txtSlo').val(data);
			  $('#txtSlo').val(JSON.stringify(data, null, 4));
			  //alert(JSON.stringify(data));
          }
       });
	},
    attachHandlers: function () {
        var that = this;
        conpaas.ui.Page.prototype.attachHandlers.call(this);
        $('#name').click(this, this.onClickName);
        
        $('#manfile').change(this, this.onChangeManifest);
        $('#appfile').change(this, this.updateName);
        $('#profilefile').change(this, this.onUploadProfile);
        $('#slofile').change(this, this.onUploadSLO);
        
        $('#profile').click(this, this.onClickProfile);
        $('#upmanfile').click(this, this.onDialog);
        $('#upappfile').click(this, this.onDialog);
        $('#upprofilefile').click(this, this.onDialog);
        $('#upslofile').click(this, this.onDialog);
        
    },
    onDialog: function(event){
		var idfileinpit = this.id.substring(2);
		$( "#"+idfileinpit ).trigger( "click" );
	},
	updateName: function(event){
		var idspanname = this.id + 'name';
		$( "#"+idspanname).html( $('#'+this.id)[0].files[0].name );
	},
    checkServices: function () {
        var that = this;
        this.poller.setLoadingText('checking services...').poll(
                function (response) {
            var service,
                services,
                i,
                continuePolling = true;
            services = response.data;
            $('#servicesWrapper').html(response.html);
            for (i = 0; i < services.length; i++) {
                service = new conpaas.model.Service(services[i].sid,
                        services[i].state, services[i].instanceRoles,
                        services[i].reachable);
                if (service.needsPolling()) {
                    that.displayInfo_(service);
                    continuePolling = false;
                }
                // HACK: attach handlers for delete buttons;
                // without using the id trick we cannot avoid using global vars
                $('#service-' + service.sid + ' .deleteService').click(
                        that.makeDeleteHandler_(service));
            }
            conpaas.ui.visible('pgstatInfo', false);
            return continuePolling;
        });
    },
    deleteService: function (service) {
        var that = this,
            servicePage = new conpaas.ui.ServicePage(this.server, service);
        servicePage.terminate(function () {
            $('#service-' + service.sid).hide();
        }, function () {
            // error
            that.poller.stop();
        });
    }
    });

    return this_module;
}(conpaas.ui || {}));

$(document).ready(function () {
    var server = new conpaas.http.Xhr(),
    page = new conpaas.ui.Dashboard(server, null);
    page.attachHandlers();
    
    // page.checkServices();
    // if (true) {
    //   // page.freezeInput(true);
    //   page.pollState(function () {
    //       window.location.reload();
    //   }, null, 10);
    // }

});
