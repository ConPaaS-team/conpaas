//$(document).ready(function () {
    //var service,
        //page,
        //sid = GET_PARAMS['sid'],
        //server = new conpaas.http.Xhr();
        //server.req('ajax/getProfilingInfo.php', {sid:sid}, 'get', function (data) {
            //// service = new conpaas.model.Service(data.sid, data.state,
            ////         data.instanceRoles, data.reachable);
            //// page = new conpaas.ui.MysqlPage(server, service);
            //// page.attachHandlers();
            //// if (page.service.needsPolling()) {
            ////     page.freezeInput(true);
            ////     page.pollState(function () {
            ////         window.location.reload();
            ////     });
            //// }
            //alert(data);
        //}, function () {
            //// error
            //window.location = 'services.php';
        //})
//});


conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.MysqlPage
     */
    this_module.GenericPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
        this.poller = new conpaas.http.Poller(server, 'ajax/getProfilingInfo.php', 'get');
        //this.setupPoller_();
    },
    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    pollState: function (onStableState, onInstableState, maxInterval) {
        var that = this;
        this.poller.poll(function (response) {
            str = '<table class="slist" cellpadding="0" cellspacing="0">'
            str += '<tr><th>Status</th><th>Configuration</th><th>Time</th><th>Cost</th></tr>'
            tdclass = 'wrapper '
            
            for (var i = 0; i < response.profiling_info.length; i++) {
                img = 'running'
                if (i == response.profiling_info.length - 1)
                    tdclass += 'last'
                str += '<tr class="service">';
                if (response.profiling_info[i].Done)
                    img='tick'
                str += '<td class="'+tdclass+'" style="border-left: 1px solid #ddd;"><img src="images/' + img + '.gif"/></td>';
                str += '<td class="'+tdclass+'">' + that.objToString(response.profiling_info[i].Configuration) + '</td>';
                //str += '<td class="'+tdclass+'">' + that.objToString(response.profiling_info[i].Arguments) + '</td>';
                if (response.profiling_info[i].Done){
                    str += '<td class="'+tdclass+'">' + response.profiling_info[i].Results.ExeTime + '</td>';
                    str += '<td class="'+tdclass+'">' + response.profiling_info[i].Results.TotalCost + '</td>';
                }else
                    str += '<td colspan="2" class="'+tdclass+'">' + '' + '</td>';
                str += '</tr>';
                
            }
            str += '</table>'; 
            
            $("#divcontent").html(str);
            //that.service.state = response.state;
            //that.service.reachable = response.reachable;
            //if (!that.service.needsPolling()) {
                //conpaas.ui.visible('pgstatInfo', false);
                //if (typeof onStableState === 'function') {
                    //onStableState(response);
                //}
                //// reached stable state
                //return true;
            //}
            //that.displayReason_();
            // returning false will cause the poller to continue polling
            if (typeof onInstableState === 'function') {
                onInstableState(response);
            }
            return false;
        }, {sid: this.service.sid}, maxInterval);
    }, 
    
    objToString: function(obj){
        str = ''
        for (var property in obj) {
            if (obj.hasOwnProperty(property)) {
                str += property + ':' + obj[property] + ', '
            }
        }
        
        return str.substring(0, str.length - 2).replace(/%/g, '');
    },
     
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
        //$('#createVolume').click(this, this.onCreateVolume);
        //$('#deleteVolume').click(this, this.onDeleteVolume);
    },
    //// handlers
    //onCreateVolume: function (event) {
        //var page = event.data,
            //volumeName = $('#volume').val();
            //owner = $('#owner').val();    
        //if(volumeName.length == 0){
            //page.showCreateVolStatus('error','There is no volume name');  
            //return;
        //}

        //if(owner.length == 0){
            //page.showCreateVolStatus('error','There is no owner');    
            //return;
        //}
        ////send the request
        //$('#createVolume').attr('disabled','disabled');
        //page.server.req('ajax/createVolume.php', {
            //sid: page.service.sid,
            //volumeName: volumeName,
            //owner: owner
        //}, 'post', function (response) {
            //// successful
            //page.showCreateVolStatus('positive', 'The Volume was created successfuly');
            //$('#createVolume').removeAttr('disabled');
            //$('#volume').val('');
            //$('#owner').val('');
            //$('.selectHint, .msgbox').hide();
        //}, function (response) {
            //// error
            //page.showCreateVolStatus('error', 'Volume was not created');
            //$('#createVolume').removeAttr('disabled');
        //});
    //},

    //onDeleteVolume: function (event) {
        //var page = event.data,
            //volumeName = $('#volume').val();
        
        //if(volumeName.length == 0){
            //page.showCreateVolStatus('error','There is no volume name');  
            //return;
        //}
        ////send the request
        //$('#deleteVolume').attr('disabled','disabled');
        //page.server.req('ajax/deleteVolume.php', {
            //sid: page.service.sid,
            //volumeName: volumeName
        //}, 'post', function (response) {
            //// successful
            //page.showCreateVolStatus('positive', 'The Volume was deleted successfuly');
            //$('#deleteVolume').removeAttr('disabled');
            //$('#volume').val('');
            //$('.selectHint, .msgbox').hide();
        //}, function (response) {
            //// error
            //page.showCreateVolStatus('error', 'Volume was deleted');
            //$('#deleteVolume').removeAttr('disabled');
        //});
    //}
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
            page = new conpaas.ui.GenericPage(server, service);
            page.attachHandlers();
            //if (page.service.needsPolling()) {
            if (true) {
                page.freezeInput(true);
                page.pollState(function () {
                    window.location.reload();
                }, null, 10);
            }
            
        }, function () {
            // error
            window.location = 'services.php';
    })
});
