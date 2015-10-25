/* Copyright (C) 2010-2013 by Contrail Consortium. */



/**
 * interaction for services.php - main dashboard
 * @require conpaas.js
 */

conpaas.ui = (function(this_module) {
  this_module.Dashboard = conpaas.new_constructor(
    /* extends */
    conpaas.ui.Page,
    /* constructor */
    function(server, application) {
      this.server = server;
      this.application = application;
      this.services = [];
      this.jplot = null;
      // this.poller = new conpaas.http.Poller(server, 'ajax/checkServices.php', 'get');
      this.poller = new conpaas.http.Poller(server, 'ajax/getProfilingInfo.php', 'get');
      this.appication_uploaded = false;
      this.constraint_nr = 0;
      this.status = '';
      this.plot_data = [];

      if (!sessionStorage.iterations)
        sessionStorage.iterations = 1;

      if (!sessionStorage.extrapolate)
        sessionStorage.extrapolate = 1;

      if (!sessionStorage.debug)
        sessionStorage.debug = 1;
      if (!sessionStorage.monitor)
        sessionStorage.monitor = 0;
    },
    /* methods */
    {
      /**
       * @param {Service} service that caused the polling to be continued
       */
      displayInfo_: function(service) {
        var info = 'at least one service is in a transient state';
        if (!service.reachable) {
          info = 'at least one service is unreachable'
        }
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
      },
      displayInfo_2: function(info) {
        $('#pgstatInfoText').html(info);
        conpaas.ui.visible('pgstatInfo', true);
      },
      pollState: function(onStableState, onInstableState, maxInterval) {
        var that = this;
        this.poller.poll(function(response) {

          if (response.ready) {

            if (!response.profile.application && !that.appication_uploaded) {
              that.services = response.profile.services;
              that.displayInfo_2('Uploading application...');
              that.uploadApplication();
              that.appication_uploaded = true;
              window.location = "application.php?aid=" + that.application.aid;
              return true;
            }
            if (response.profile.state == 'RUNNING')
              return true;

            var type = that.services[Object.keys(that.services)[0]];
            var profile = response.profile.pm;
            if (response.profile.state == 'PROFILING'){
            
              $("#" + type + "_status").html('Profiling');
              $("#" + type + "_led").attr('src', 'images/ledorange.png');

            
              if (profile.extrapolations.length > 0 && profile.experiments.length > 0)
                that.displayInfo_2('Extrapolating...');
              else
                that.displayInfo_2('Profiling...');
            }

            that.updateProfileInfo(profile);

            if (response.profile.state == 'PROFILED') {
              conpaas.ui.visible('pgstatInfo', false);
              var downlink = '<a class="button small" href="ajax/getProfilingInfo.php?aid=' + that.application.aid + '&format=file">Download profile</a><br/><br/>';
              $("#downloadProfile").html(downlink);
              $("#downloadProfile").show();
              $("#slodiv").show(500);
              $("#" + type + "_status").html('Profiled');
              $("#" + type + "_led").attr('src', 'images/ledgreen.png');

              return true;
            }


            // // $("#divProfile").html(JSON.stringify(response));
          } else {
            that.displayInfo_2('Starting application manager...');
          }

          if (typeof onInstableState === 'function') {
            onInstableState(response);
          }
          return false;
        }, {
          aid: this.application.aid
        }, maxInterval);
      },
      pollApplication: function(onStableState, onInstableState, maxInterval) {
        var that = this;
        params = {}
        if (this.application)
          params.aid = this.application.aid;

        this.poller.poll(function(response) {
          // alert(response);


          that.displayInfo_2('Executing application...');
          //if terminated return true
          for (var type in response.servinfo) {
            if (response.servinfo.hasOwnProperty(type)) {
              status = response.servinfo[type].state;
              if (status == 'TERMINATED') {
                $("#" + type + "_status").html('Application terminated');
                $("#" + type + "_led").attr('src', 'images/ledgray.png');
              } else if (status == 'PROFILED'){
                $("#" + type + "_status").html('Profiled');
                $("#" + type + "_led").attr('src', 'images/ledgreen.png');
              } else if (status == 'PROFILED'){
                $("#" + type + "_status").html('Running');
                $("#" + type + "_led").attr('src', 'images/ledgreen.png');
              }
            }
          }

          if (response.frontend != null && response.frontend.length > 0) {
            $("#applink").attr("href", response.frontend)
            $("#applink").show()
          }

          if (!Array.isArray(response.execinfo)) { //bad way of checking if the application was executed or not
            var et = that.myround(response.execinfo.execution_time, 4),
              tc = that.myround(response.execinfo.total_cost, 4),
              err = that.myround(((that.et - et) / et) * 100, 2);
            $("#acExecTime").html(et + '');
            $("#acCost").html(tc + '');
            $("#absError").html(err + '');
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

        }, params, maxInterval);

      },

      updateProfileInfo: function(profile) {
        var that = this;
        var str = '<table class="slist" cellpadding="0" cellspacing="0" style="/*border: 1px solid;*/">',
          tdclass = 'wrapper ';

        // str += '<thead style="display:block;"><tr style="background:#F2F2F2"><th width="30" style="padding:5px">Status</th><th width="50">Config</th><th width="80" style="padding:5px">Time(sec)</th><th width="70" style="padding:5px">Cost(&euro;)</th><th width="80">Monitor</th></tr></thead><tbody id="prof_table" style="height:200px; overflow:auto; overflow-x:hidden; /*overflow-y:scroll;*/ display:block;">';
        str += '<thead style="display:block;"><tr style="background:#F2F2F2"><th width="30" style="padding:5px">Status</th><th width="60">Config</th><th width="50" style="padding:5px">Time(sec)</th><th width="60" style="padding:5px">Cost(&euro;)</th><th width="60">Monitor</th></tr></thead><tbody id="prof_table" style="height:200px; overflow:auto; overflow-x:hidden; /*overflow-y:scroll;*/ display:block;">';

        var exps = [];
        var pareto = [];
        var extras = [];
        var failed = [];
        var ij = '';
        var tr_class = ''
        exps_ext = [profile.experiments, profile.extrapolations];
        for (var j = 0; j < exps_ext.length; j++) {
          expers = exps_ext[j];
          if (j == 1)
            tr_class = 'extrapolation_row'
          for (var i = 0; i < expers.length; i++) {
            var img = 'running';
            if (j == 1 && i == expers.length - 1)
              tdclass += 'last';
            str += '<tr class="service exps ' + tr_class + '">';
            if (expers[i].Done == undefined || expers[i].Done) {
              img = 'tick';
              if (!expers[i].Success)
                img = 'fail';
            }
            ij = i + '-' + j;
            str += '<td align="center" class="' + tdclass + '" style="/*border-left: 1px solid #ddd;*/ width:35px; border:none;"><img src="images/' + img + '.gif" style="width:16px"/></td>';
            str += '<td align="center" class="' + tdclass + ' config" data-tipped-options="position: \'left\', inline: \'config_' + ij + '\'" style="border:none; width:35px;">'
            str += '<img style="height:18px" src="images/conf.png" />'
              //str += '<div id="config_'+i+'-'+j+'" style="display:none">' + /*this.objToString(expers[i].Configuration)*/ this.render_config(expers[i].Configuration) + '</div></td>';
            str += '<div id="config_' + ij + '" style="display:none">' + /*this.objToString(expers[i].Configuration)*/ this.render_config2(expers[i].Configuration) + '</div></td>';
            if (expers[i].Done == undefined || expers[i].Done) {
              tc = this.myround(expers[i].Results.TotalCost, 4);
              et = this.myround(expers[i].Results.ExeTime, 4);

              str += '<td align="center" class="' + tdclass + ' et" style="border:none; width:60px;">' + et + '</td>';
              str += '<td align="center" class="' + tdclass + ' cst" style="border:none; width:54px;">' + tc + '</td>';
              str += '<td id="monitor_' + ij + '" align="center" class="' + tdclass + ' monitor" data-tipped-options="position: \'right\', inline: \'target_monitor_' + ij + '\'" style="border:none;">';
              if (this.hasMonitor(expers[i].Monitor)) {
                str += '<img style="width:24px; margin-right:0px;" src="images/monitor.png" />';
                str += '<div id="target_monitor_' + ij + '" style="display:none;">' + this.set_monitor_ph(expers[i].Monitor, ij) + '</div></td>';
              } else {
                str += '<img style="width:24px; margin-right:20px;" src="images/off.png" />';
                str += '<div id="target_monitor_' + ij + '" style="display:none;">No monitoring information</div></td>';
              }

              if (!expers[i].Success) {
                failed.push([tc, et]);

              } else {
                if (j == 0)
                  exps.push([tc, et]);
                else
                  extras.push([tc, et]);
              }

            } else
              str += '<td colspan="3" class="' + tdclass + '" style="border:none;">' + '' + '</td>';
            str += '</tr>';
          }
        }


        str += '</tbody></table>';

        tuples = [];

        extra_pareto = [profile.extrapolations, profile.pareto];
        for (var k = 0; k < extra_pareto.length; k++) {
          ex_pa = extra_pareto[k];
          for (var i = 0; i < ex_pa.length; i++) {
            if (!ex_pa[i].Done)
              continue;
            if (!ex_pa[i].Success)
              continue;
            extra_conf = this.conf_to_string(ex_pa[i].Configuration);
            extratc = this.myround(ex_pa[i].Results.TotalCost, 4);
            extraet = this.myround(ex_pa[i].Results.ExeTime, 4);
            for (var j = 0; j < profile.experiments.length; j++) {
              if (!profile.experiments[j].Success)
                continue;
              exp_conf = this.conf_to_string(profile.experiments[j].Configuration);
              exptc = this.myround(profile.experiments[j].Results.TotalCost, 4);
              expet = this.myround(profile.experiments[j].Results.ExeTime, 4);
              if (extra_conf == exp_conf)
                tuples.push([
                  [exptc, expet],
                  [extratc, extraet]
                ])
            }
          }
        }

        for (var i = 0; i < profile.pareto.length; i++)
          if (profile.pareto[i].Done == undefined || profile.pareto[i].Done)
          // pareto.push([profile.pareto[i].Results.TotalCost.toFixed(3), profile.pareto[i].Results.ExeTime.toFixed(3)]);
            pareto.push([this.myround(profile.pareto[i].Results.TotalCost, 4), this.myround(profile.pareto[i].Results.ExeTime, 4)]);

        that.render_failed(failed);

        if (profile.experiments.length > 0 || profile.pareto.length > 0 || profile.extrapolations.length > 0) {
          $("#divProfileTable").html(str);
          $("#toggleCorrelation").show();
          $("#prof_table").animate({
            scrollTop: $('#prof_table')[0].scrollHeight
          }, 1000);
          Tipped.create('.config');

          Tipped.create('.monitor', {
            skin: 'white',
            onShow: function(content, element) {
              if ($(element)[0].wtf == undefined) {
                id = $(content).find('div')[0].id;
                ij = id.split("_")[2];
                i = ij.split("-")[0];
                j = ij.split("-")[1];
                exp = exps_ext[j][i];
                if (that.hasMonitor(exp.Monitor))
                  that.prepare_plot(exp, ij);
                $(element)[0].wtf = 'wtf';
              }
            },
          });
          this.plot_data=[exps, extras, pareto, [], tuples]
          that.plot(exps, extras, pareto, [], tuples);
        }

      },
      hasMonitor: function(monitor) {
        for (var address in monitor) {
          if (monitor.hasOwnProperty(address)) {
            for (var metr in monitor[address]) {
              if (monitor[address].hasOwnProperty(metr)) {
                if (monitor[address][metr].length > 0)
                  return true;
              }
            }
          }
        }
        return false;
      },
      prepare_plot: function(exp, ij) {
        var conf = exp.Configuration;
        var monitor = exp.Monitor;
        var metrix_dict = {};
        var address_dict = {};
        metrix_names = this.get_metrix_names(monitor);
        for (var i = 0; i < metrix_names.length; i++) {
          metrix_dict[metrix_names[i]] = [];
          address_dict[metrix_names[i]] = [];
        }

        for (var address in monitor) {
          if (monitor.hasOwnProperty(address)) {
            for (var metr in monitor[address]) {
              if (monitor[address].hasOwnProperty(metr)) {
                metrix_dict[metr].push(monitor[address][metr]);
                address_dict[metr].push(address);
              }
            }
          }
        }

        for (var i = 0; i < metrix_names.length; i++) {
          for (var j = 0; j < metrix_dict[metrix_names[i]].length; j++) {
            for (var k = 0; k < metrix_dict[metrix_names[i]][j].length; k++)
              metrix_dict[metrix_names[i]][j][k] = [k, metrix_dict[metrix_names[i]][j][k]]
          }
          this.plotMonitor('monplot_' + metrix_names[i] + '_' + ij, metrix_dict[metrix_names[i]], address_dict[metrix_names[i]]);
        }

      },
      get_metrix_names: function(monitor) {
        var metrix = '';

        for (var address in monitor) {
          if (monitor.hasOwnProperty(address)) {
            for (var metr in monitor[address]) {
              if (monitor[address].hasOwnProperty(metr)) {
                metrix += metr + ',';
                metrix = metrix.split(',').filter(function(item, i, allItems) {
                  return i == allItems.indexOf(item);
                }).join(',');
              }
            }
          }
        }
        metrix = metrix.slice(0, metrix.length - 1);
        return metrix.split(',').sort();
      },
      set_monitor_ph: function(monitor, ij) {

        var cols = 4;
        var toret = '<table border="1" cellspacing="0" cellpadding="2">';
        metr_arr = this.get_metrix_names(monitor);
        var row_closed = false;
        for (var i = 0; i < metr_arr.length; i++) {
          if (i % cols == 0) {
            toret += '<tr>';
            row_closed = false;
          }
          toret += '<td>';
          toret += '<div align="center" style="width:100%">' + metr_arr[i] + '</div>';
          toret += '<div id="monplot_' + metr_arr[i] + '_' + ij + '" style="width:300px; height:200px"></div>';

          toret += '</td>';
          if (i % cols == cols - 1) {
            toret += '</tr>';
            row_closed = true;
          }

        }
        if (!row_closed)
          toret += '</tr>';


        toret += '</table>';
        // alert(toret);
        return toret;
      },
      objToString: function(obj) {
        var str = '';
        for (var property in obj) {
          if (obj.hasOwnProperty(property)) {
            str += property + ':' + obj[property] + ', ';
          }
        }

        return str.substring(0, str.length - 2).replace(/%/g, '');
      },
      render_config: function(config) {
        var toret = '';
        for (var i = 0; i < config.length; i++) {
          toret += '<strong>' + config[i].Type + '</strong>:<br>'
          for (var property in config[i].Attributes) {
            if (config[i].Attributes.hasOwnProperty(property)) {
              toret += "&emsp;" + property + ':<strong>' + config[i].Attributes[property] + '</strong><br/>';
            }
          }
          if (i < config.length - 1)
            toret += '<hr>'
        }
        return toret;
      },
      render_failed: function(failed) {
        var toret = '<table style="margin-top:10px"><tr><td><strong>Failed configurations:</strong>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;'
        toret += '<span style="font-weight: bold; color:#E10818">(' + failed.length + ')</span></td><td>'
        toret += '<table border="0" cellspacing="3" cellpadding="0" style="margin-right: 10px;">';
        var cols = 10;
        var row_closed = false;
        for (var i = 0; i < failed.length; i++) {
          if (i % cols == 0) {
            toret += '<tr>';
            row_closed = false;
          }
          tc = failed[i][0];
          et = failed[i][1];
          toret += '<td class="fail">';
          toret += '<img src="images/error.png"/>';
          toret += '<div style="display:none">' + tc + '|' + et + '</div>';
          toret += '</td>';
          if (i % cols == cols - 1) {
            toret += '</tr>';
            row_closed = true;
          }
        }
        if (!row_closed)
          toret += '</tr>';
        toret += '</table></td></tr></table>';
        if (failed.length > 0) {
          $('#failed').html(toret);
          $('.fail').click(this, this.highlight_error);
        }else
          $('#failed').html('');
        // return toret;
      },

      render_config2: function(config) {
        var toret = '<table border="1" cellspacing="0" cellpadding="2">';
        var cols = 4;
        var row_closed = false;
        for (var i = 0; i < config.length; i++) {
          if (i % cols == 0) {
            toret += '<tr>';
            row_closed = false;
          }
          toret += '<td>';
          toret += '<strong>' + config[i].Type + '</strong>:<br>'
          for (var property in config[i].Attributes) {
            if (config[i].Attributes.hasOwnProperty(property)) {
              //toret += "&emsp;"+property + ':<strong>' + config[i].Attributes[property] + '</strong><br/>';
              toret += property + ':<strong>' + config[i].Attributes[property] + '</strong><br/>';
            }
          }
          toret += '</td>';
          if (i % cols == cols - 1) {
            toret += '</tr>';
            row_closed = true;
          }
        }
        if (!row_closed)
          toret += '</tr>';
        toret += '</table>';
        return toret;
      },

      conf_to_string: function(config) {
        var toret = '';
        for (var i = 0; i < config.length; i++) {
          toret += config[i].Type + ' ( '
          for (var property in config[i].Attributes) {
            if (config[i].Attributes.hasOwnProperty(property)) {
              toret += property + ':' + config[i].Attributes[property] + ' ';
            }
          }

          toret += ')'
          if (i < config.length - 1)
            toret += ', '
        }
        return toret;
      },

      myround: function(nr, dec) {
        return parseFloat(nr.toFixed(dec));
      },
      highlight_error: function() {
        var page = arguments[0].data;
        var data = $($(this).find('div')[0]).html().split('|');
        page.highlight_entry(data);
      },
      highlight_entry: function(data) {
        $('#prof_table').scrollTop(0);
        row = $("#prof_table tr.exps").filter(function() {
          var time = $(this).find("td.et").eq(0).html();
          var cost = $(this).find("td.cst").eq(0).html();
          return data[0] + "" == cost && data[1] + "" == time;
          //return $(this).text() == data[0];
        });

        index = row.index();
        var tpos = $('#prof_table').offset().top;
        var ypos = $('#prof_table tr.exps:eq(' + index + ')').offset().top;
        //alert("ypos:" + ypos + " tpos:"+ tpos);
        $('#prof_table').animate({
          scrollTop: ypos - tpos
        }, 100);
        $(row).addClass("highlight", 500);
        setTimeout(function() {
          $(row).removeClass("highlight", 2000);
        }, 1000);
      },

      uploadApplication: function() {
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
          success: function(data) {
            // alert(data)
            var type = that.services[Object.keys(that.services)[0]];
            $("#" + type + "_led").attr('src', 'images/ledgreen.png');
            $("#" + type + "_status").html('Ready');
            conpaas.ui.visible('pgstatInfo', false);
            that.onHideUpload();
            $("#profilediv").show(500);
          }
        });

      },


      plotMonitor: function(div, res, names) {
        toplot = []
        options = {
          series: [],

          axes: {
            xaxis: {
              label: 'Time',
              labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
              min: 0
            },
            yaxis: {
              label: 'Usage',
              labelRenderer: $.jqplot.CanvasAxisLabelRenderer,
              min: 0,
              max: 100
            }
          },
          highlighter: {
            show: true,
            sizeAdjust: 7.5
          },
          legend: {
            show: true,
            placement: 'outside',
            location: 's',
            marginTop: '0px'
          },
          cursor: {
            show: true,
            zoom: true,
            showTooltip: false
          }
        };
        for (var i = 0; i < res.length; i++) {
          toplot.push(res[i]);
          name = names[i];
          if (name.length > 15)
            name = name.substring(name.length-16)
          options.series.push({
            showMarker: false,
            lineWidth: 1,
            rendererOptions: {
              smooth: true
            },
            label: name
          });
          // options.seriesColors.push('#999999');
        }
        $.jqplot(div, toplot, options);
      },
      plot: function(experiments, extrapolations, pareto, selected, tuples) {
        if (this.jplot != null) {
          if (selected.length > 0 || (experiments == null && pareto == null )) {
            experiments = this.jplot.series[0].data;
            extrapolations = this.jplot.series[1].data;
            pareto = this.jplot.series[2].data;
            if (tuples == null){
              tuples = [];
              for (var i = 3; i < this.jplot.series.length; i++) {
                tuples.push(this.jplot.series[i].data);
              }
            }

          }

          this.jplot.destroy();
          updated_data = [experiments, extrapolations, pareto, selected];
          // tuples_drown_first_time = this.jplot.options.series.length <= 4;
          for (var i = 0; i < tuples.length; i++) {
            updated_data.push(tuples[i]);
            // if(tuples_drown_first_time){
            this.jplot.options.series.push({
              showMarker: false,
              lineWidth: 1,
              linePattern: 'dashed',
              rendererOptions: {
                smooth: true
              }
            });
            this.jplot.options.seriesColors.push('#999999');
            // }
          }
          this.jplot.data = updated_data;

          this.jplot.replot(updated_data, {
            resetAxes: true
          });

        } else {

          var toplot = [experiments, extrapolations, pareto, selected];
          for (var i = 0; i < toplot.length; i++)
            if (toplot[i].length == 0)
              toplot[i] = [
                []
              ]

          var options = {

            series: [{
                showLine: false,
                markerOptions: {
                  size: 4,
                  style: "x"
                }
              }, {
                showLine: false,
                markerOptions: {
                  size: 4,
                  style: "x"
                }
              }, {
                showMarker: false,
                lineWidth: 3,
                rendererOptions: {
                  smooth: true
                }
              }, {
                showLine: false,
                markerOptions: {
                  size: 9,
                  style: "circle"
                }
              }

            ],
            seriesColors: ['#999999', '#ED772D', '#4990D6', '#ED1515'],
            axes: {
              xaxis: {
                label: 'Cost (euro)',
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer
              },
              yaxis: {
                label: 'Time (sec)',
                labelRenderer: $.jqplot.CanvasAxisLabelRenderer
              }
            },
            highlighter: {
              show: true,
              sizeAdjust: 7.5
            },
            cursor: {
              show: true,
              zoom: true,
              showTooltip: false
            }
          };
          for (var i = 0; i < tuples.length; i++) {
            toplot.push(tuples[i]);
            options.series.push({
              showMarker: false,
              lineWidth: 1,
              linePattern: 'dashed',
              rendererOptions: {
                smooth: true
              }
            });
            options.seriesColors.push('#999999');
          }


          this.jplot = $.jqplot('divProfileChart', toplot, options);
        }
      },

      makeDeleteHandler_: function(service) {
        var that = this;
        return function() {
          that.deleteService(service);
        };
      },
      saveName: function(newName, onSuccess, onError) {
        this.server.req('ajax/renameApplication.php', {
            name: newName
          }, 'post',
          onSuccess, onError);
      },
      onClickName: function(event) {
        var page = event.data;
        var newname = prompt("Enter a new name", $('#name').html());
        if (!newname) {
          return;
        }
        page.saveName(newname, function() {
          $('#name').html(newname);
        })
      },

      onClickProfile: function(event) {
        var that = event.data;
        $.ajax({
          url: 'ajax/profile.php',
          data: {
            'aid': that.application.aid,
            'debug': sessionStorage.debug,
            'monitor': sessionStorage.monitor,
            'iterations': sessionStorage.iterations,
            'extrapolate': sessionStorage.extrapolate,
          },
          processData: true,
          contentType: false,
          dataType: 'json',
          type: 'GET',

          success: function(data) {
            that.pollState(function() {
              window.location.reload();
            }, null, 10);

          }
        });


      },
      onChangeManifest: function(event) {
        var that = event.data;
        var idspanname = this.id + 'name';
        $("#" + idspanname).html($('#' + this.id)[0].files[0].name);
        var file = $('#manfile')[0].files[0];
        var formData = new FormData();
        formData.append('manifest', file, file.name);
        formData.append('format', 'file');
        that.updateManifestInfo(formData);

      },

      updateManifestInfo: function(formData) {
        var that = this;
        $.ajax({
          url: 'ajax/parseManifest.php',
          data: formData,
          processData: false,
          contentType: false,
          dataType: 'json',
          type: 'POST',
          success: function(data) {
            $('#name').html(data.application_name);
            var status = 'Service not initialized';
            var ledcolor = 'gray';
            if (that.status == 'running') {
              status = 'Running';
              ledcolor = 'green';
            }

            var html = '<div class="services"><table class="slist" cellspacing="1" cellpadding="0">';
            for (var i = 0; i < data.services.length; i++) {
              html += '<tr class="service"><td class="colortag colortag-stopped"></td> \
             <td class="wrapper last"> \
               <div class="icon"><img src="images/' + data.services[i].module_type + '.png" height="64"></div> \
               <div class="content" style="padding-left:20px"> \
                  <div class="title">' + data.services[i].module_name + '<img id="' + data.services[i].module_type + '_led" class="led" title="initialized" src="images/led' + ledcolor + '.png"></div> \
                  <div id="' + data.services[i].module_type + '_status" class="actions">' + status + '</div> \
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
      onUploadProfile: function(event) {
        var that = event.data;

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
          success: function(data) {
            that.updateProfileInfo(data);
            $("#downloadProfile").hide();
            $("#slodiv").show(500);
            //alert(JSON.stringify(data));
          }
        });
      },

      onUploadManifest: function(event) {
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
          success: function(data) {
            that.application = new conpaas.model.Application(data.appid);
            that.pollState(function() {
              window.location.reload();
            }, null, 10);
          }
        });

      },
      onUploadSLO: function(event) {
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
          success: function(data) {
            $('#txtSlo').val(JSON.stringify(data, null, 4));
          }
        });
      },

      onPreConfiguration: function(event) {
        var that = event.data;
        var group = event.target.getAttribute('group');
        var tol = 0.0001;

        last = that.jplot.series[2].data.length - 1;
        middle = 1;
        min_prod = 0;
        if (that.jplot.series[2].data.length == 1) {
          min_prod = that.jplot.series[2].data[0][0] * that.jplot.series[2].data[0][1];
          middle = 0;
        } else
          min_prod = that.jplot.series[2].data[1][0] * that.jplot.series[2].data[1][1];

        for (var i = 1; i < that.jplot.series[2].data.length - 1; i++) {
          if (that.jplot.series[2].data[i][0] * that.jplot.series[2].data[i][1] < min_prod)
            middle = i;
        }

        minCost = that.jplot.series[2].data[0][0] + tol;
        maxCost = that.jplot.series[2].data[last][0] - tol;
        midCost = that.jplot.series[2].data[middle][0] + tol;


        var valid = true;
        if (group == "cheap")
          slo = {
            'optimize': 'execution_time',
            conds: [{
              'key': 'cost',
              'op': '<=',
              'val': minCost
            }]
          };
        else if (group == "balanced")
          slo = {
            'optimize': 'execution_time',
            conds: [{
              'key': 'cost',
              'op': '<=',
              'val': midCost
            }]
          };
        else if (group == "fast")
          slo = {
            'optimize': 'execution_time',
            conds: [{
              'key': 'cost',
              'op': '>=',
              'val': maxCost
            }]
          };
        else
          valid = false;

        if (valid)
          that.showConfiguration(slo);
      },

      onClickShowConfiguration: function(event) {
        var that = event.data;
        slo = {
          'optimize': '',
          conds: []
        };
        slo.optimize = $("#optimizeSelect").val();
        for (var i = 0; i < 100; i++) {
          cond = {};
          if ($("#ccol_" + i).length) {
            cond.key = $("#ccol_" + i).children('select').eq(0).val();
            cond.op = $("#ccol_" + i).children('select').eq(1).val();
            cond.val = $("#ccol_" + i).children('input').eq(0).val();
            slo.conds.push(cond);
          }
        }

        that.showConfiguration(slo);

      },

      showConfiguration: function(slo) {
        var that = this;
        $.ajax({
          url: 'ajax/uploadSLO.php',
          data: {
            'aid': that.application.aid,
            'service': 'echo',
            'slo': slo
          },
          // processData: false,
          // contentType: false,
          dataType: 'json',
          type: 'POST',

          success: function(data) {
            conf = $.parseJSON(data);
            conf = conf.result.conf;
            if (conf != null && conf.length > 0) {
              conf = conf[0]
              tc = that.myround(conf.Results.TotalCost, 4);
              et = that.myround(conf.Results.ExeTime, 4);
              $("#selectedConfig").html(that.conf_to_string(conf.Configuration));

              $("#esExecTime").html(et + '');
              $("#esCost").html(tc + '');

              selected = [
                [tc, et]
              ];
              that.tc = tc;
              that.et = et;
              that.plot(null, null, null, selected, null);
            } else {
              $("#selectedConfig").html("No configuration can satisfy this SLO");
              $("#esExecTime").html("-");
              $("#esCost").html("-");
              that.plot(null, null, null, [], null);
            }
          }
        });
      },

      onExecuteSlo: function(event) {

        var that = event.data;
        $.ajax({
          url: 'ajax/executeSLO.php',
          data: {
            'aid': that.application.aid
          },
          // data: {'aid': 1},
          processData: true,
          contentType: false,
          dataType: 'json',
          type: 'GET',
          success: function(data) {
            that.poller = new conpaas.http.Poller(that.server, 'ajax/getApplicationInfo.php', 'get');
            that.pollApplication(function() {
              window.location.reload();
            }, null, 5);
          }
        });
      },

      onShowUpload: function() {
        $('#uploaddiv').show(500);
        $('#showuploaddiv').hide();
      },

      onHideUpload: function() {
        $('#uploaddiv').hide(300);
        $('#showuploaddiv').show(300);
        $("#showuploaddiv").animate({
          "top": "-=10px"
        }, "fast");
        $("#showuploaddiv").animate({
          "top": "+=10px"
        }, "fast");
      },

      addConstraints: function(event) {
        var that = event.data;
        that.constraint_nr++;
        var constraint = '<tr id="crow_' + that.constraint_nr + '"><td></td><td id="ccol_' + that.constraint_nr + '" style="background:#F2F2F2"><select><option value="cost">Cost</option><option value="execution_time">Execution time</option></select> ';
        constraint += '<select><option value="<">&lt;</option><option value="<=">&le;</option><option value=">">&gt;</option><option value=">=">&ge;</option><option value="==">=</option></select> ';
        constraint += '<input type="text" style="width:50px; text-align:center" value="0.0" /> <img name="crem" id="crem_' + that.constraint_nr + '" src="images/remove.png" style="cursor:pointer"/></td></tr>';
        $('#constraintTable tr:last').before(constraint);
        $("#crem_" + that.constraint_nr).click(that.remConstraints);

      },


      remConstraints: function(event) {
        var id = event.target.id.split("_")[1];
        $('#crow_' + id).remove();
      },

      attachHandlers: function() {
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

        $('#correlation').change(this, this.showHideCorrelation);
        $('.pre-configure').click(this, this.onPreConfiguration);

        // $("img[name='crem']").click(this, this.remConstraints);

      },
      showHideCorrelation:function(event) {
        var that = event.data;
        if($('#correlation')[0].checked){
          that.plot(null, null, null, that.jplot.data[3], that.plot_data[4]);
        }else
        {
          // alert('hide')
          that.plot(null, null, null, that.jplot.data[3], []);
        }

        
        
      },

      clearPopup: function(event) {
        var that = event.data;
        $('.popup.visible').addClass('transitioning').removeClass('visible');
        $('html').removeClass('overlay');

        setTimeout(function() {
          $('.popup').removeClass('transitioning');
        }, 200);
        if (that.onclosepopup) {
          that.onclosepopup();
          that.onclosepopup = null;
        }
      },


      showSettings: function(event) {
        var that = event.data;
        var debug = '';
        var monitor = '';
        var extrapolate = '';
        if (sessionStorage.debug == 1)
          debug = 'checked';
        if (sessionStorage.monitor == 1)
          monitor = 'checked';
        if (sessionStorage.extrapolate == 1)
          extrapolate = 'checked';
        html = '<table border="0" style="width:60%">';
        html += '<tr><td>Extrapolate:</td> <td align="center"><input id="extrapolate" type="checkbox" name="extrapolate" ' + extrapolate + '></td></tr>';
        html += '<tr><td>Debugging:</td> <td align="center"><input id="debug" type="checkbox" name="debug" ' + debug + '></td></tr>';
        html += '<tr><td>Monitoring:</td> <td align="center"><input id="monitor" type="checkbox" name="monitor" ' + monitor + '></td></tr>';
        html += '<tr><td>Iterations:</td> <td align="center"><input id="iterations" type="number" value="' + sessionStorage.iterations + '" style="width:40px"/></td></tr>';
        html += '</table> <br>';

        $('.popup-content').html(html);
        that.showPopup(this);
        that.onclosepopup = that.closeSettings;
      },

      closeSettings: function() {
        sessionStorage.debug = 0;
        sessionStorage.monitor = 0;
        sessionStorage.extrapolate = 0;
        if ($('#debug').is(":checked"))
          sessionStorage.debug = 1;
        if ($('#monitor').is(":checked"))
          sessionStorage.monitor = 1;
        if ($('#extrapolate').is(":checked"))
          sessionStorage.extrapolate = 1;
        sessionStorage.iterations = $('#iterations').val();
      },

      showPopup: function(source) {
        var that = source;
        $('html').addClass('overlay');
        var activePopup = $(that).attr('data-popup-target');
        $(activePopup).addClass('visible');
      },

      onDialog: function(event) {
        var idfileinpit = this.id.substring(2);
        $("#" + idfileinpit).trigger("click");
      },
      updateName: function(event) {
        var idspanname = this.id + 'name';
        $("#" + idspanname).html($('#' + this.id)[0].files[0].name);
      },
      checkServices: function() {
        var that = this;
        this.poller.setLoadingText('checking services...').poll(
          function(response) {
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

      deleteService: function(service) {
        var that = this,
          servicePage = new conpaas.ui.ServicePage(this.server, service);
        servicePage.terminate(function() {
          $('#service-' + service.sid).hide();
        }, function() {
          // error
          that.poller.stop();
        });
      }
    });

  return this_module;
}(conpaas.ui || {}));

$(document).ready(function() {
  var server = new conpaas.http.Xhr(),
    page = new conpaas.ui.Dashboard(server, null);
  page.attachHandlers();

  $('#divProfileChart').bind('jqplotDataClick',
    function(ev, seriesIndex, pointIndex, data) {
      page.highlight_entry(data);
    });

  //Tipped.create('#profile', 'Some tooltip text');
  var aid = GET_PARAMS['aid'];

  if (typeof aid !== "undefined") {
    page.server.req('ajax/checkApplications.php', {
      'aid': aid
    }, 'get', function(response) {
      var app_data = response.data;
      page.application = new conpaas.model.Application(app_data.application.aid);
      if (app_data.application.manager.length > 0)
        page.status = 'running';

      var formData = new FormData();
      formData.append('manifest', app_data.manifest);
      formData.append('format', 'text');
      page.updateManifestInfo(formData);

      page.services = app_data.profile.services;
      $("#profilediv").show(500);
      // if (app_data.profile.pm.experiments.length > 0)
      //   $("#slodiv").show(500);

      page.onHideUpload();
      // page.updateProfileInfo(app_data.profile.pm);
      page.pollState(function () {
        window.location.reload();
      }, null, 10);

    }, function(error) {
      page.displayError(error.name, error.details);
    });

  } else {
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