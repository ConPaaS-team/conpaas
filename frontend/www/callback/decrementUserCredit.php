<?php 
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

ignore_user_abort(true);

require_once('../__init__.php');
require_once('../UserData.php');
require_once('../ServiceData.php');
require_once('../ServiceFactory.php');


/* accept POST requests only */
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    die();
}

$response = 'empty';

if(!isset($_POST['sid']) || !isset($_POST['decrement'])) {
    $response = array('error' => 'Missing arguments');
}
else if ($_POST['decrement'] < 1) {
    $response = array('error' => 'Invalid arguments');
}
else {
    try {
        /* accept requests from manager nodes only */
        $service_data = ServiceData::getServiceById($_POST['sid']);
        $service = ServiceFactory::create($service_data);
        $manager_host = parse_url($service->getManager(), PHP_URL_HOST);
        /* test source of request is from a manager node */
        if (gethostbyname($manager_host) !== $_SERVER['REMOTE_ADDR']) {
            $response = array('error' => 'Not allowed');
        }
        else {
            $ret = UserData::updateUserCredit($service->getUID(), -$_POST['decrement']);
            if ($ret === false) {
                $response = array('error' => 'Not enough credit');
            }
            else {
                $response = array('error' => null);
            }
        }
    } catch (Exception $e) {
        $response = array(
    		'error' => 'Internal error'
        );
    }
}

echo json_encode($response);
?>
