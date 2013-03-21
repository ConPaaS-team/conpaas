/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.MysqlPage
     */
    this_module.XtreemFSPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.setupPoller_();
    },
    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        $('#createVolume').click(this, this.onCreateVolume);
        $('#deleteVolume').click(this, this.onDeleteVolume);
    },
    showCreateVolStatus: function (type, message) {
        var otherType = (type === 'positive') ? 'error' : 'positive';
        $('#VolumeStat').removeClass(otherType).addClass(type)
            .html(message)
            .show();
        setTimeout(function () {
            $('#VolumeStat').fadeOut();
        }, 3000);
    },
    // handlers
    onCreateVolume: function (event) {
		var page = event.data,
			volumeName = $('#volume').val();
	        owner = $('#owner').val();	
		if(volumeName.length == 0){
			page.showCreateVolStatus('error','There is no volume name');	
			return;
		}

		if(owner.length == 0){
			page.showCreateVolStatus('error','There is no owner');	
			return;
		}
		//send the request
		$('#createVolume').attr('disabled','disabled');
        page.server.req('ajax/createVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName,
            owner: owner
        }, 'post', function (response) {
            // successful
            page.showCreateVolStatus('positive', 'The Volume was created successfuly');
            $('#createVolume').removeAttr('disabled');
            $('#volume').val('');
            $('#owner').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showCreateVolStatus('error', 'Volume was not created');
            $('#createVolume').removeAttr('disabled');
        });
    },

    onDeleteVolume: function (event) {
		var page = event.data,
			volumeName = $('#volume').val();
		
		if(volumeName.length == 0){
			page.showCreateVolStatus('error','There is no volume name');	
			return;
		}
		//send the request
		$('#deleteVolume').attr('disabled','disabled');
        page.server.req('ajax/deleteVolume.php', {
            sid: page.service.sid,
            volumeName: volumeName
        }, 'post', function (response) {
            // successful
            page.showCreateVolStatus('positive', 'The Volume was deleted successfuly');
            $('#deleteVolume').removeAttr('disabled');
            $('#volume').val('');
            $('.selectHint, .msgbox').hide();
        }, function (response) {
            // error
            page.showCreateVolStatus('error', 'Volume was deleted');
            $('#deleteVolume').removeAttr('disabled');
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
        page = new conpaas.ui.XtreemFSPage(server, service);
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
