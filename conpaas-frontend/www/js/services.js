
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
        this.services = [];
        this.jplot = null;
        // this.poller = new conpaas.http.Poller(server, 'ajax/checkServices.php', 'get');
        this.poller = new conpaas.http.Poller(server, 'ajax/getProfilingInfo.php', 'get');
        this.appication_uploaded = false;
        this.constraint_nr = 0;
        this.status = '';

        if (!sessionStorage.iterations) 
            sessionStorage.iterations = 1;
        
        if (!sessionStorage.debug) 
            sessionStorage.debug = 1;
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
                if (!response.profile.application && !that.appication_uploaded){
                  that.services = response.profile.services;
                  that.displayInfo_2('Uploading application...');
                  that.uploadApplication();
                  that.appication_uploaded = true;
                  window.location = "application.php?aid=" +that.application.aid;
                  return true;
                }                

                that.displayInfo_2('Profiling...');
                var type = that.services[Object.keys(that.services)[0]];
                $("#"+type+"_status").html('Profiling'); 
                $("#"+type+"_led").attr('src', 'images/ledorange.png');

                var profile = response.profile.pm;
                that.updateProfileInfo(profile);
                
                if(response.profile.state == 'RUNNING'){
                    conpaas.ui.visible('pgstatInfo', false);
                    var downlink = '<a class="button small" href="ajax/getProfilingInfo.php?aid='+that.application.aid+'&format=file">Download profile</a><br/><br/>';
                    $("#downloadProfile").html(downlink); 
                    $("#downloadProfile").show();
                    $("#slodiv").show(500);
                    $("#"+type+"_status").html('Profiled'); 
                    $("#"+type+"_led").attr('src', 'images/ledgreen.png');

                    return true;
                }


                // // $("#divProfile").html(JSON.stringify(response));
            }else{
                that.displayInfo_2('Starting application manager...');
            }

            if (typeof onInstableState === 'function') {
                onInstableState(response);
            }
            return false;
        }, {aid: this.application.aid}, maxInterval);
    },
    pollApplication: function (onStableState, onInstableState, maxInterval) {
        var that = this;
        this.poller.poll(function (response) {
            that.displayInfo_2('Executing application...');
            //if terminated return true
            for (var type in response.servinfo) {
              if (response.servinfo.hasOwnProperty(type)) {
                 status = response.servinfo[type].state;
                 if (status =='TERMINATED'){
                      $("#"+type+"_status").html('Application terminated'); 
                      $("#"+type+"_led").attr('src', 'images/ledgray.png');
                 }else{
                      $("#"+type+"_status").html('Running'); 
                      $("#"+type+"_led").attr('src', 'images/ledgreen.png');
                 }
              }
            }

            if (response.frontend.length > 0) {
                $("#applink").attr("href", response.frontend)
                $("#applink").show()
            }

            if(!Array.isArray(response.execinfo)){ //bad way of checking if the application was executed or not
                var et = that.myround(response.execinfo.execution_time,4),
                tc = that.myround(response.execinfo.total_cost,4),
                err = that.myround(((that.et - et) / et) * 100, 2); 
                $("#acExecTime").html(et+'');
                $("#acCost").html(tc+'');
                $("#absError").html(err+'');
                // var html = 'Actual execution time: <span>'+et+'</span> min &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Actual cost: <span>'+tc+'</span> &euro; &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; &epsilon;: <span>'+err+'</span> %';
                // $("#exeResult").html(html);
                // $("#exeResult").show();

                conpaas.ui.visible('pgstatInfo', false);
                return true;
            }


            if (typeof onInstableState === 'function') {
                onInstableState(response);
            }
            return false;
            // }
         }, {aid: this.application.aid}, maxInterval);
      // }, {aid: 1}, maxInterval);
    },  


    updateProfileInfo: function(profile){
      var str = '<table class="slist" cellpadding="0" cellspacing="0" style="/*border: 1px solid;*/">',
      tdclass = 'wrapper ';
      
      str += '<tr style="background:#F2F2F2"><th width="30" style="padding:5px">Status</th><th width="255">Configuration</th><th width="50" style="padding:5px">Time(min)</th><th width="50" style="padding:5px">Cost(&euro;)</th></tr>';

      var exps = [];
      var pareto = [];

      for (var i = 0; i < profile.experiments.length; i++) {
        var img = 'running';
        if (i == profile.experiments.length - 1)
          tdclass += 'last';
        str += '<tr class="service">';
        if (profile.experiments[i].Done == undefined || profile.experiments[i].Done)
          img='tick';
        str += '<td align="center" class="'+tdclass+'" style="/*border-left: 1px solid #ddd;*/ border:none;"><img src="images/' + img + '.gif"/></td>';
        str += '<td align="center" class="'+tdclass+'" style="border:none;">' + this.objToString(profile.experiments[i].Configuration) + '</td>';
        //str += '<td class="'+tdclass+'">' + that.objToString(response.profiling_info[i].Arguments) + '</td>';
        if (profile.experiments[i].Done == undefined || profile.experiments[i].Done){
          tc = this.myround(profile.experiments[i].Results.TotalCost,4);
          et = this.myround(profile.experiments[i].Results.ExeTime, 4);

          str += '<td align="center" class="'+tdclass+'" style="border:none;">' + et + '</td>';
          str += '<td align="center" class="'+tdclass+'" style="border:none;">' + tc + '</td>';
          // exps.push([profile.experiments[i].Results.TotalCost.toFixed(3), profile.experiments[i].Results.ExeTime.toFixed(3)]);
          // exps.push([profile.experiments[i].Results.TotalCost, profile.experiments[i].Results.ExeTime]);
          exps.push([tc, et]);

        }else
          str += '<td colspan="2" class="'+tdclass+'" style="border:none;">' + '' + '</td>';
        str += '</tr>';

        
      }
      str += '</table>'; 
      
      
      for (var i = 0; i < profile.pareto.length; i++) 
        if(profile.pareto[i].Done == undefined || profile.pareto[i].Done)
            // pareto.push([profile.pareto[i].Results.TotalCost.toFixed(3), profile.pareto[i].Results.ExeTime.toFixed(3)]);
            pareto.push([this.myround(profile.pareto[i].Results.TotalCost,4), this.myround(profile.pareto[i].Results.ExeTime,4)]);

      if(exps.length > 0 || pareto.length > 0){
        $("#divProfileTable").html(str); 
        $("#divProfileTable").animate({ scrollTop: $('#divProfileTable')[0].scrollHeight}, 1000);
        this.plot(exps, pareto,[]);
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
    myround: function(nr, dec){
      return parseFloat(nr.toFixed(dec));
    },

    
    uploadApplication: function(){
      var that = this;
      var appfile = $('#appfile')[0].files[0];
      var formData = new FormData();
      formData.append('appfile', appfile, appfile.name);
      formData.append('aid', this.application.aid);
      formData.append('sid', Object.keys(this.services)[0]);
      $.ajax({
          url: 'ajax/uploadApplication.php',
          data: formData,
          cache: false,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
            // alert(data)
            var type = that.services[Object.keys(that.services)[0]];
            $("#"+type+"_led").attr('src', 'images/ledgreen.png');
            $("#"+type+"_status").html('Ready'); 
            conpaas.ui.visible('pgstatInfo', false);
            that.onHideUpload();
            $("#profilediv").show(500);
          }
       });

    },

    highlight: function(selection){
        var x = this.jplot.axes.xaxis.series_u2p(selection[0]);
        var y = this.jplot.axes.yaxis.series_u2p(selection[1]);
        var r = 5;
        var drawingCanvas = $(".jqplot-highlight-canvas")[0]; //$(".jqplot-series-canvas")[0];
        var context = drawingCanvas.getContext('2d');
        context.clearRect(0, 0, drawingCanvas.width, drawingCanvas.height); //plot.replot();            
        context.strokeStyle = "#ED1515";
        context.fillStyle = "#ED1515";
        context.beginPath();
        context.arc(x, y, r, 0, Math.PI * 2, true);
        context.closePath();
        context.stroke();
        context.fill();
    },
    plot: function (experiments, pareto, selected){
        if (this.jplot != null)
        {
            if(selected.length > 0 || (experiments == null && pareto == null) )
            {
                experiments = this.jplot.series[0].data;
                pareto = this.jplot.series[1].data;
            }

            this.jplot.destroy();
            this.jplot.series[0].data = experiments;
            this.jplot.series[1].data = pareto;
            this.jplot.series[2].data = selected;
            this.jplot.replot({resetAxes:true});
            // if(selected.length > 0){
            //   this.highlight(this.jplot.series[2].data[0]);
            // }
        }else{
            this.jplot = $.jqplot('divProfileChart',  [experiments, pareto, selected],
            { 
            series:[ 
                  {showLine:false, markerOptions: { size: 4, style:"x" }},
                  {showMarker:false, lineWidth: 3, rendererOptions: {smooth: true} },
                  {showLine:false, markerOptions: { size: 9, style:"circle" }}
                  
                  ],
              seriesColors:['#ED772D', '#4990D6', '#ED1515'],   
              axes:{
                xaxis:{
                  label:'Cost (euro)',
                  labelRenderer: $.jqplot.CanvasAxisLabelRenderer
                },
                yaxis:{
                  label:'Time (min)',
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
        $.ajax({
          url: 'ajax/profile.php',
          data: {'aid': that.application.aid, 'debug':sessionStorage.debug, 'iterations':sessionStorage.iterations},
          processData: true,
          contentType: false,
          dataType: 'json',
          type: 'GET',

          success: function(data){
            that.pollState(function () {window.location.reload();}, null, 5);
            
          }
        });
  

    },
    onChangeManifest: function (event) {
        var that = event.data; 
        var idspanname = this.id + 'name';
        $( "#"+idspanname).html( $('#'+this.id)[0].files[0].name );
        var file = $('#manfile')[0].files[0];
        var formData = new FormData();
        formData.append('manifest', file, file.name);
        formData.append('format', 'file');
        that.updateManifestInfo(formData);
        
    },

    updateManifestInfo: function(formData){
        var that = this;
        $.ajax({
          url: 'ajax/parseManifest.php',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
            $('#name').html(data.applicatio_name);
            var status = 'Service not initialized';
            var ledcolor = 'gray';
            if (that.status == 'running'){
               status = 'Running';
               ledcolor = 'green';
            }
            
            var html = '<div class="services"><table class="slist" cellspacing="1" cellpadding="0">';
            for(var i = 0; i < data.services.length; i++){
             html += '<tr class="service"><td class="colortag colortag-stopped"></td> \
             <td class="wrapper last"> \
               <div class="icon"><img src="images/'+data.services[i].module_type+'.png" height="64"></div> \
               <div class="content" style="padding-left:20px"> \
                  <div class="title">'+data.services[i].module_name+'<img id="'+data.services[i].module_type+'_led" class="led" title="initialized" src="images/led'+ledcolor+'.png"></div> \
                  <div id="'+data.services[i].module_type+'_status" class="actions">'+status+'</div> \
               </div> \
               <div class="statistic"> \
                  <a id="applink" style="display:none;" target="blank" href="#"><img style="width:32px; margin-top:7px;" src="images/link.png"></a> \
                  <!--div class="statcontent"><img src="images/throbber-on-white.gif"></div> \
                  <div class="note">loading...</div--> \
               </div> \
               <div class="clear"></div> \
            </td></tr>';
            }
            html += '<tr><td colspan="2"><div id="exeResult" class="execres" style="display:none">Actual execution time: <span>-</span>,  Actual cost: <span>-</span></div></td></tr>';
            html += '</table></div>';

            $('#servicesWrapper').html(html);
          }
       });
    },
    onUploadProfile: function(event){  
      var that = event.data; 
      //var profile = response.profile.profile;
          //that.updateProfileInfo(profile);
      //var idspanname = this.id + 'name';
      //$( "#"+idspanname).html( $('#'+this.id)[0].files[0].name );
        var file = $('#profilefile')[0].files[0];
        var formData = new FormData();
        formData.append('profile', file, file.name);
        formData.append('aid', that.application.aid);
        // formData.append('aid', 1);
        $.ajax({
          url: 'ajax/uploadProfile.php',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data){
              that.updateProfileInfo(data);
              $("#downloadProfile").hide();
              $("#slodiv").show(500);
        //alert(JSON.stringify(data));
          }
       });
    },
  
  onUploadManifest: function(event){
    var that = event.data; 
        var manfile = $('#manfile')[0].files[0];
        var appfile = $('#appfile')[0].files[0];
        var formData = new FormData();
        formData.append('manfile', manfile, manfile.name);
        formData.append('appfile', appfile, appfile.name);
        
        that.displayInfo_2('Starting application manager...');
        
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
            that.pollState(function () {
                window.location.reload();
                }, null, 5);

            // setTimeout(function(){
            //   that.pollState(function () {
            //     window.location.reload();
            //     }, null, 5);
            // }, 1000);
            // alert(that.application.aid);
            
          }
        });
  },
  onUploadSLO: function(event)
    {  
        var that = event.data; 
        var file = $('#slofile')[0].files[0];
        var formData = new FormData();
        formData.append('slo', file, file.name);
        formData.append('service', 'echo');
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

  onPreConfiguration: function(event){
    var that = event.data;
    var group = event.target.getAttribute('group');
    var tol = 0.0001;

    last = that.jplot.series[1].data.length - 1; 
    middle = Math.round(last/2); 

    minCost = that.jplot.series[1].data[0][0] + tol;
    maxCost = that.jplot.series[1].data[last][0] - tol;
    midCost = that.jplot.series[1].data[middle][0] + tol;

    var valid = true;
    if(group=="cheap")
      slo = {'optimize':'execution_time', conds:[{'key':'cost', 'op':'<=', 'val':minCost}]};
    else if (group=="balanced")
      slo = {'optimize':'execution_time', conds:[{'key':'cost', 'op':'<=', 'val':midCost}]};
    else if (group=="fast")
      slo = {'optimize':'execution_time', conds:[{'key':'cost', 'op':'>=', 'val':maxCost}]};
    else
      valid = false;
    
    if (valid)
      that.showConfiguration(slo);
    // alert(minCost);
  },

   onClickShowConfiguration: function(event){
        var that = event.data; 
        slo = {'optimize':'', conds:[]};
        slo.optimize = $("#optimizeSelect").val();
        for(var i = 0; i < 100; i++){
          cond = {};
            if ( $("#ccol_"+i).length ){
              cond.key = $("#ccol_"+i).children('select').eq(0).val();   
              cond.op = $("#ccol_"+i).children('select').eq(1).val();   
              cond.val = $("#ccol_"+i).children('input').eq(0).val();   
              slo.conds.push(cond);
            }
        }

        that.showConfiguration(slo);
        
    },

    showConfiguration: function(slo)
    { 
        var that = this; 
        $.ajax({
          url: 'ajax/uploadSLO.php',
          data: {'aid': that.application.aid, 'service':'echo', 'slo':slo},
          // processData: false,
          // contentType: false,
          dataType: 'json',
          type: 'POST',

          success: function(data){
              conf = $.parseJSON( data );
              conf = conf.result.conf;
              // var html = '';
              if (conf != null){
                  tc = that.myround(conf.Results.TotalCost,4);
                  et = that.myround(conf.Results.ExeTime, 4);
                  $("#selectedConfig").html(that.objToString(conf.Configuration));

                  $("#esExecTime").html(et+'');
                  $("#esCost").html(tc+'');
                  // html += 'Selected configuration: <span>'+ that.objToString(conf.Configuration) +'</span> <br/>';
                  // html += 'Estimated execution time: <span>'+et+'</span> min &nbsp;&nbsp;&nbsp; Estimated cost: <span>'+tc+'</span> &euro;';
                  
                  // selected = [[conf.Results.TotalCost.toFixed(3) , conf.Results.ExeTime.toFixed(3)]];
                  selected = [[tc , et]];
                  that.tc = tc;
                  that.et = et;
                  that.plot(null, null, selected);
              }else{
                $("#selectedConfig").html("No configuration can satisfy this SLO");
                $("#esExecTime").html("-");
                $("#esCost").html("-");
                that.plot(null, null, []);
              }
          }
        });
    },

    onExecuteSlo: function(event)
    {  

        var that = event.data; 
        $.ajax({
          url: 'ajax/executeSLO.php',
          data: {'aid': that.application.aid},
          // data: {'aid': 1},
          processData: true,
          contentType: false,
          dataType: 'json',
          type: 'GET',
          success: function(data){
            that.poller = new conpaas.http.Poller(that.server, 'ajax/getApplicationInfo.php', 'get');
            that.pollApplication(function () {
                window.location.reload();
            }, null, 5);
          }
       });
    },

    onShowUpload: function () {
        $('#uploaddiv').show(500);
        $('#showuploaddiv').hide();
    },

    onHideUpload: function () {
        $('#uploaddiv').hide(300);
        $('#showuploaddiv').show(300);
        $( "#showuploaddiv" ).animate({ "top": "-=10px" }, "fast" );
        $( "#showuploaddiv" ).animate({ "top": "+=10px" }, "fast" );
    },

    addConstraints: function (event) {
      var that = event.data; 
      that.constraint_nr ++;
      var constraint = '<tr id="crow_'+that.constraint_nr+'"><td></td><td id="ccol_'+that.constraint_nr+'" style="background:#F2F2F2"><select><option value="cost">Cost</option><option value="execution_time">Execution time</option></select> '; 
         constraint += '<select><option value="<">&lt;</option><option value="<=">&le;</option><option value=">">&gt;</option><option value=">=">&ge;</option><option value="==">=</option></select> ';
         constraint += '<input type="text" style="width:50px; text-align:center" value="0.0" /> <img name="crem" id="crem_'+that.constraint_nr+'" src="images/remove.png" style="cursor:pointer"/></td></tr>';
      $('#constraintTable tr:last').before(constraint);
      $("#crem_"+that.constraint_nr).click(that.remConstraints);
      
    },


    remConstraints: function (event) {
      var id = event.target.id.split("_")[1];
      $('#crow_'+id).remove();
    },

    attachHandlers: function () {
        var that = this;
        conpaas.ui.Page.prototype.attachHandlers.call(this);
        $('#name').click(this, this.onClickName);
        
        $('#manfile').change(this, this.onChangeManifest);
        $('#appfile').change(this, this.updateName);
        $('#profilefile').change(this, this.onUploadProfile);
        $('#slofile').change(this, this.onUploadSLO);
       
        $('#uploadManifest').click(this, this.onUploadManifest);


        $('#profile').click(this, this.onClickProfile);
        $('#upmanfile').click(this, this.onDialog);
        $('#upappfile').click(this, this.onDialog);
        $('#upprofilefile').click(this, this.onDialog);
        $('#upslofile').click(this, this.onDialog);
        $('#showConfiguration').click(this, this.onClickShowConfiguration);
        $('#executeSlo').click(this, this.onExecuteSlo);
        $('#showuploaddiv').click(this, this.onShowUpload);
        $('#hideuploaddiv').click(this, this.onHideUpload);
        
        $('#addConstraints').click(this, this.addConstraints);
        $('#settings').click(this, this.showSettings);
        $('.popup-exit').click(this, this.clearPopup);

        
        $('.pre-configure').click(this, this.onPreConfiguration);
        // $("img[name='crem']").click(this, this.remConstraints);

  },

  clearPopup: function (event) {
      var that = event.data;  
      $('.popup.visible').addClass('transitioning').removeClass('visible');
      $('html').removeClass('overlay');

      setTimeout(function () {
          $('.popup').removeClass('transitioning');
      }, 200);
      if (that.onclosepopup){
        that.onclosepopup();
        that.onclosepopup = null;
      }
  },   


  showSettings: function(event){
      var that = event.data;
      var checked = '';
      if (sessionStorage.debug == 1)
        checked = 'checked';
      html = '<table border="0" style="width:60%">';
      html += '<tr><td>Debugging:</td> <td align="center"><input id="debug" type="checkbox" name="debug" '+checked+'></td></tr>';
      html += '<tr><td>Iterations:</td> <td align="center"><input id="iterations" type="number" value="'+sessionStorage.iterations+'" style="width:40px"/></td></tr>';
      html += '</table> <br>';

      $('.popup-content').html(html);
      that.showPopup(this);
      that.onclosepopup = that.closeSettings;
  },

  closeSettings: function(){
     // $('#setting-div').html($('.popup-content').html());
     sessionStorage.debug = 0 ;
     if ($('#debug').is(":checked"))
         sessionStorage.debug = 1 ;
     sessionStorage.iterations = $('#iterations').val();
     // $('.popup-content').html('');
     // $('#iterations').val(iterations);
  },

  showPopup: function(source){
      var that = source;
      $('html').addClass('overlay');
      var activePopup = $(that).attr('data-popup-target');
      $(activePopup).addClass('visible');
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
    var aid = GET_PARAMS['aid'];
   
    if(typeof aid !== "undefined"){
      page.server.req('ajax/checkApplications.php', {'aid':aid}, 'get', function (response) {
          var app_data = response.data;
          page.application =  new conpaas.model.Application(app_data.application.aid);
          if (app_data.application.manager.length > 0)
            page.status = 'running';

          var formData = new FormData();
          formData.append('manifest', app_data.manifest);
          formData.append('format', 'text');
          page.updateManifestInfo(formData);
        
          page.services = app_data.profile.services;
          $("#profilediv").show(500);
          if (app_data.profile.pm.experiments.length > 0)
            $("#slodiv").show(500);

          page.onHideUpload();
          page.updateProfileInfo(app_data.profile.pm);
         
      }, function (error) {
        page.displayError(error.name, error.details);
      });

    }else{
      $('#name').html('New application');
    }


    
    


    // page.checkServices();
    // if (true) {
    //   // page.freezeInput(true);
    //   page.pollState(function () {
    //       window.location.reload();
    //   }, null, 10);
    // }

});
