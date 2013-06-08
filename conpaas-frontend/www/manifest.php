<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

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
           <tr class="service">
             <td class="description"> <img src="images/owncloud.png" height="32" /></td>
             <td class="radio" width="150px"><input type="radio" name="type" value="owncloud" /> OwnCloud</td>
             <td class="info" width="480px"> OwnCloud version 5.0 deployment </td>
           </tr>
           <tr class="service">
             <td class="description"> <img src="images/wordpress.png" height="32" /></td>
             <td class="radio" width="150px"><input type="radio" name="type" value="wordpress" /> WordPress</td>
             <td class="info" width="480px"> WordPress version 3.5 deployment </td>
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
