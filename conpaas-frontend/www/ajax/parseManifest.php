<?php

require_once('../__init__.php');
if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

try {

	if (isset($_POST['format']) && $_POST['format']=="file") {
		$fileContent = file_get_contents($_FILES['manifest']['tmp_name']);
		$manifest = json_decode($fileContent);
	}else{
		$manifest = json_decode($_POST['manifest']);
	}

	// $services = '<div class="services"><table class="slist" cellspacing="1" cellpadding="0">';

	$arrman = array();		
	$arrman['applicatio_name'] = $manifest->ApplicationName;
	$arrman['services'] = array();
	$i=0;
	foreach ($manifest->Modules as $value)
	{
		// $services .= '<tr class="service"><td>'.$value->ModuleName.'</td><td>'.$value->ModuleType.'</td><td>Not initialized</td></tr>';
		// $services .= '<tr class="service"><td class="colortag colortag-stopped"></td>
		// 		<td class="wrapper last">
		// 		   <div class="icon"><img src="images/'.$value->ModuleType.'.png" height="64"></div>
		// 		   <div class="content" style="padding-left:20px">
		// 			  <div class="title">'.$value->ModuleName.'<img id="'.$value->ModuleType.'_led" class="led" title="initialized" src="images/ledgray.png"></div>
		// 			  <div id="'.$value->ModuleType.'_status" class="actions">Service not initialized</div>
		// 		   </div>
		// 		   <div class="statistic">
		// 			  <!--div class="statcontent"><img src="images/throbber-on-white.gif"></div>
		// 			  <div class="note">loading...</div-->
		// 		   </div>
		// 		   <div class="clear"></div>
		// 		</td></tr>';
		$arrman['services'][$i] = array();
		$arrman['services'][$i]['module_type'] = $value->ModuleType;
		$arrman['services'][$i]['module_name'] = $value->ModuleName;
		$i++;
	}
	// $services .= '</table></div>';

	// echo $services;
	echo json_encode($arrman);

	

} catch (Exception $e) {
	echo json_encode(array(
		'error' => $e->getMessage()

	));
}

?>
