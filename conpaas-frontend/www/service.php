<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */


require_once('__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui');
require_module('ui/page');
require_module('ui/service');

$sid = $_GET['sid'];
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);
$page = PageFactory::create($service);

if ($service->getUID() !== $page->getUID()) {
    $page->redirect('index.php');
}

$state = $page->getState();
$backendType = $service->getType();

?>
<?php echo $page->renderDoctype(); ?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  	<?php echo $page->renderContentType(); ?>
    <?php echo $page->renderTitle(' - '.$backendType); ?>
    <?php echo $page->renderIcon(); ?>
    <?php echo $page->renderHeaderCSS(); ?>
  </head>
<body class="<?php echo $page->getBrowserClass(); ?>">
	<?php echo $page->renderHeader(); ?>
	<div class="pagecontent">
		<?php echo $page->renderTopMenu(); ?>
		<?php echo $page->renderContent(); ?>
	</div>
<?php echo $page->renderFooter(); ?>
<?php echo $page->generateJSGetParams(); ?>
<?php echo $page->renderJSLoad(); ?>
</body>
</html>
