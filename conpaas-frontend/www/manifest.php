<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_once('__init__.php');
require_module('ui/page');

$page = new Page();
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
   <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
      <title>ConPaaS - Upload new manifest</title>
      <link type="text/css" rel="stylesheet" href="conpaas.css" />
      <?php echo $page->renderIcon(); ?>
      <script src="js/jquery-1.5.js"></script>
      <script src="js/jquery.form.js"></script>
      <script src="js/manifest.js"></script>
   </head>
   <body class="<?php echo $page->getBrowserClass(); ?>">
      <?php echo $page->renderHeader(); ?>

      <div class="pagecontent createpage">
         <div class="pageheader">
            <h1> <img src="images/create.png" /> Deploy application</h1>
            <div class="clear"></div>
         </div>

         <table class="form" cellspacing="0" cellpading="0">
            <tr>
               <form id="fileForm" enctype="multipart/form-data" action="ajax/uploadManifest.php">
                  Choose the specification file to upload: <input name="specfile" type="file"><br>
               </form>
            </tr>
            <tr>
               <td class="description" style="vertical-align: middle;">
                  <img class="loading" src="images/icon_loading.gif" style="display: none;" />
               </td>
               <td class="description"></td>
               <td>
                  <i id="status"></i>
                  <i id="error" style="display: none;"></i>
               </td>
            </tr>
         </table>

         <table class="form" cellspacing="0" cellpading="0">
           <!--
           <tr class="service">
             <td class="description"> <img src="images/owncloud.png" height="32" /></td>
             <td class="radio" width="150px"><input type="radio" name="type" value="owncloud" /> OwnCloud</td>
             <td class="info" width="480px"> OwnCloud version 5.0 deployment </td>
           </tr>
            -->
           <tr class="service">
             <td class="description"> <img src="images/wordpress.png" height="32" /></td>
             <td class="radio" width="150px"><input type="radio" name="type" value="wordpress" /> WordPress</td>
             <td class="info" width="480px"> WordPress version 3.5 deployment </td>
           </tr>
           <tr class="service">
             <td class="description"> <img src="images/mediawiki.png" height="32" /></td>
             <td class="radio" width="150px"><input type="radio" name="type" value="mediawiki" /> MediaWiki</td>
             <td class="info" width="480px"> MediaWiki version 1.21 deployment </td>
           </tr>
         </table>

         <a id="deploy" class="button" href="javascript: void(0);">
                  <img src="images/play.png" style="vertical-align: top;"/> Deploy Application
         </a>

         <br>
         <br>
         <br>
         <br>

      </div>

      <?php echo $page->renderFooter(); ?>
   </body>
</html>
