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

$(document).ready(function () {
    var service,
        page,
        sid = GET_PARAMS['sid'],
        server = new conpaas.http.Xhr();
    server.req('ajax/getService.php', {sid: sid}, 'get', function (data) {
        service = new conpaas.model.Service(data.sid, data.state,
                data.instanceRoles, data.reachable);
        page = new conpaas.ui.ServicePage(server, service);
        page.attachHandlers();
        if (page.service.needsPolling()) {
            page.freezeInput(true);
            page.pollState(function () {
                window.location.reload();
            });
        }
    }, function () {
        // error
        window.location = 'index.php';
    })
});