conpaas.ui = (function (this_module) {
    /**
     * conpaas.ui.CdsPage
     */
    this_module.CdsPage = conpaas.new_constructor(
    /* extends */conpaas.ui.ServicePage,
    /* constructor */function (server, service) {
        this.server = server;
        this.service = service;
    },
    /* methods */{
    /**
     * @override conpaas.ui.ServicePage.attachHandlers
     */
    attachHandlers: function () {
        var that = this;
        conpaas.ui.ServicePage.prototype.attachHandlers.call(this);
    },
    drawMap: function (regions) {
        var dataArray = [['Region', 'Edge Locations']];
        var options = {
                legend: 'none',
                displayMode: 'markers',
                colorAxis: {colors: ['blue', 'green']},
                sizeAxis: {minValue: -5,  maxSize: 5}
        };
        var chart = new google.visualization.GeoChart(
                document.getElementById('map-container'));
        regions.forEach(function (region) {
            dataArray.push([region.state, region.edge_locations]);
        });
        chart.draw(google.visualization.arrayToDataTable(dataArray), options);
    }
    });
    
    return this_module;
}(conpaas.ui || {}));

google.load('visualization', '1', {'packages': ['geochart']});
google.setOnLoadCallback(function () {
    // init
    var service,
        page,
        sid = GET_PARAMS['sid'],
        server = new conpaas.http.Xhr();
    server.req('ajax/getService.php', {sid: sid}, 'get', function (data) {
        service = new conpaas.model.Service(data.sid, data.state,
            data.instanceRoles, data.reachable);
        page = new conpaas.ui.CdsPage(server, service);
        page.attachHandlers();
    });
    // geo chart
    server.req('ajax/cds_getRegions.php', {sid: sid}, 'get',
            function (regions) {
        page.drawMap(regions);
    })
    var data = google.visualization.arrayToDataTable([
        ['Region', 'Edge Locations'],
        ['Northern California', 1],
        ['Ireland', 0],
    ]);

});
