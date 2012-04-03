/*
 * Copyright (C) 2010-2012 Contrail consortium.
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
/**
 * @require conpaas.js, servicepage.js
 */
conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.TaskFarmPage
     */
    this_module.TaskFarmPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
        this.chart = null;
        this.samplingResults = null;
    },
    /* methods */{
    freezeInput: function (freeze) {
        var buttonsSelector = '#startSample, #startExec';
        if (freeze) {
            $(buttonsSelector).attr('disabled', 'disabled');
        } else {
            $(buttonsSelector).removeAttr('disabled');
        }
    },
    loadSamplingResults: function () {
        var that = this;
        this.server.req('ajax/taskfarm_getSamplingResults.php',
                {sid: this.service.sid}, 'get', function (response) {
                    that.samplingResults = response;
                    $('#samplings').empty();
                    $.each(that.samplingResults, function (index, sampling) {
                        $('#samplings').append($("<option></option>")
                            .attr("value", sampling.timestamp)
                            .text(sampling.name));
                    });
                });
    },
    drawChart: function (schedules) {
        var data = new google.visualization.DataTable(),
            options,
            that = this;
        data.addColumn('number', 'Execution Time');
        data.addColumn('number', 'Cost');
        $.each(schedules, function (index, schedule) {
            budget = parseInt(schedule.split('\t')[1]);
            console.log(schedule.split('\t'));
            data.addRow([(index + 1) * 15, budget]);
        });
        options = {
            width: 400, height: 240,
            title: 'Execution Options',
            pointSize: 3,
            hAxis: {
                title: 'Time Needed (minutes)',
                minValue: 0
            },
            vAxis: {
                title: 'Budget/Cost'
            }
        };
        this.chart = new google.visualization.LineChart(
                document.getElementById('executionChart'));
        google.visualization.events.addListener(chart, 'select', function () {
            var selectedSampling,
                scheduleIndex;
            selectedSampling = that.samplingResults[$('#samplings').attr(
                'selectedIndex')];
            scheduleIndex = that.chart.getSelection()[0].row;
            $('#scheduleDetails').html(
                    selectedSampling.schedules[scheduleIndex]);
            console.log(scheduleIndex);
        });
        this.chart.draw(data, options);
    },
    attachHandlers: function () {
        var that = this;
        // first attach parent handlers
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        // ajaxify the file form
        $('#fileForm').ajaxForm({
            dataType: 'json',
            success: function(response) {
                $('.additional .loading').toggleClass('invisible');
                $('.additional .positive').show();
                setTimeout(function () {
                    $(".additional .positive").fadeOut();
                }, 1000);
                $('#botFile').val('');
                $('#xmlFile').val('');
                that.displayInfo('performing sampling...');
                that.freezeInput(true);
                that.pollState(function () {
                    window.location.reload();
                }, function () {
                    that.freezeInput(false);
                });
            },
            error: function(response) {
                that.poller.stop();
                // show the error
                that.server.handleError({name: 'service error',
                    details: response.error});
            }
        });
        $('#startSample').click(function () {
            if ($('#botFile').val() == '') {
                alert('Please choose a .bot file');
                return;
            }
            if ($('#xmlFile').val() == '') {
                alert('Please choose a .xml file');
                return;
            }
            $('.additional .loading').toggleClass('invisible');
            $('#fileForm').submit();
        });
        $('#samplings').change(this, this.onSampleChange);
        $('#startExec').click(this, this.onStartExec);
    },
    onSampleChange: function (event) {
        var page = event.data,
            selectedSampling;
        selectedSampling = $('#samplings').attr('selectedIndex');
        options = page.samplingResults[selectedSampling].schedules;
        page.drawChart(options);
    },
    onStartExec: function (event) {
        var page = event.data,
            executionOption,
            selections = page.chart.getSelection();
        if (selections.length == 0) {
            alert('Please select an execution option');
            return;
        }
        executionOption = selections[0];
        page.server.req('ajax/taskfarm_runExecution.php', {
            sid: page.service.sid,
            schedulesFile: page.samplingResults[$('#samplings').attr('selectedIndex')].timestamp,
            scheduleNo: executionOptions.row
        }, 'post', function (response) {
            page.displayInfo('performing sampling...');
            page.freezeInput(true);
            page.pollState(function () {
                window.location.reload();
            }, function () {
                page.freezeInput(false);
            });            
        });
    }
    });

    return this_module;
}(conpaas.ui || {}));

// load the google visualization API
google.load('visualization', '1.0', {'packages':['corechart']});

$(document).ready(function () {
    var service,
        page,
        sid = GET_PARAMS['sid'],
        server = new conpaas.http.Xhr();

    server.req('ajax/getService.php', {sid: sid}, 'get', function (data) {
        service = new conpaas.model.Service(data.sid, data.state,
                data.instanceRoles, data.reachable);
        page = new conpaas.ui.TaskFarmPage(server, service);
        page.attachHandlers();
        page.loadSamplingResults();
    });
});