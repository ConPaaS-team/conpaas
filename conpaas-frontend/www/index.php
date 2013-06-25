<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('logging');
require_module('application');
require_module('ui/page/apppage');
require_module('ui/application');

$page = new Apppage();
?>
<?php echo $page->renderDoctype(); ?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <?php echo $page->renderContentType(); ?>
    <?php echo $page->renderTitle(' - Index'); ?>
    <?php echo $page->renderIcon(); ?>
    <?php echo $page->renderHeaderCSS(); ?>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">
	<?php echo $page->renderHeader(); ?>
  	<div class="pagecontent">
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
