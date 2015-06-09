<?php

require_once('../__init__.php');
require_module('application');

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

try {	
	$aid = $_POST['aid'];
	$application_data = ApplicationData::getApplicationById($_SESSION['uid'], $aid);
	$application = new Application($application_data);

	$service = $_POST['service'];
	if ($service == 'echo'){
		// $fileContent = file_get_contents($_FILES['slo']['tmp_name']);
		//upload it to the application manager
		// echo $fileContent;
		$slo  =  $_POST['slo'];
		$optimize = $slo['optimize'];
		$conditions = '';
		foreach ($slo['conds'] as $cond) {
    		if ($cond['key'] == "cost")
    			$cond['key'] = "budget";

    		$conditions .='"%'.$cond['key'];
    		$conditions .= $cond['op'];
    		$conditions .= $cond['val'].'", ';
		}
		$conditions = substr($conditions, 0, -2);

		$slocontent = <<<END
{
    "SLO": {
        "ExecutionArgs": [
            {
                "Value": "parameters.txt"
            }
        ],
        "Objective": {
            "Constraints": [
                $conditions
            ],
            "Optimization": "%$optimize"
        }
    }
}
END;
		

	}else{
		$slocontent = $_POST['slo'];
	}

	$slopath = "/tmp/slo.json";
	$slofile = fopen($slopath, "w");
	fwrite($slofile, $slocontent);
	fclose($slofile);
	
	$res = $application->upload_slo($slopath);
	
	// print $res
	print json_encode($res);

} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage()
	));
}




?>
