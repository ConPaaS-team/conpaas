<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui/page/dashboard');
require_module('ui/service');

if (isset($_GET['aid'])) {
	$_SESSION['aid'] = $_GET['aid'];
} else if (! isset($_SESSION['aid'])) {
	$_SESSION['aid'] = 1;
}

$page = new Dashboard();
$services = ServiceData::getServicesByUser($page->getUID(), $_SESSION['aid']);

?>
<?php echo $page->renderDoctype(); ?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <?php echo $page->renderContentType(); ?>
    <?php echo $page->renderTitle(' - Services'); ?>
    <?php echo $page->renderIcon(); ?>
    <?php echo $page->renderHeaderCSS(); ?>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">
	<?php echo $page->renderHeader(); ?>
	<div class="pagecontent">
		<?php echo $page->renderTopMenu(); ?>
		<div class="pageheader">
			<?php echo $page->renderPageHeader(); ?>
		</div>
		<div id="servicesWrapper">
		</div>
	</div>
	<?php echo $page->renderFooter(); ?>
	<?php echo $page->renderJSLoad(); ?>
  </body>
</html>
