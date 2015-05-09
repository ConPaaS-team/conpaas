<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('logging');
require_module('ui/page');


$page = new ResourcePage();
?>
<?php echo $page->renderDoctype(); ?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <?php echo $page->renderContentType(); ?>
    <?php echo $page->renderTitle(' - Resources'); ?>
    <?php echo $page->renderIcon(); ?>
    <?php echo $page->renderHeaderCSS(); ?>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">
  <?php echo $page->renderHeader(); ?>
    <div class="pagecontent">
      <div id="resourcesWrapper" style="padding:40px">
      </div>
    </div>
    <?php echo $page->renderFooter(); ?>
    <?php echo $page->renderJSLoad(); ?>
  </body>
</html>
