<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */

require_once('__init__.php');
require_module('ui/page/createpage');


$page = new CreatePage();

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
      <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>ConPaaS - add new service </title>
    <link type="text/css" rel="stylesheet" href="css/conpaas.css" />
    <?php echo $page->renderIcon(); ?>
    <script src="js/jquery-1.5.js"></script>
    <script src="js/conpaas.js"></script>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">

    <?php echo $page->renderHeader(); ?>

      <div class="pagecontent createpage">
        <div class="pageheader">
          </div>
        <div class="selectHint">
            please select one of the services below <img width="12px" src="images/lookdown.png" />
        </div>
          <table class="form" cellspacing="0" cellpading="0">
              <div class="serviceheader">
                 Web Hosting
              </div>
              <tr class="service">
                  <td class="description"> <img src="images/php.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="php" /> php</td>
                  <td class="info"> PHP version 5.3 with Nginx </td>
              </tr>
              <tr class="service">
                  <td class="description"> <img src="images/java.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="java" /> java</td>
                  <td class="info"> Apache Tomcat 6.0 servlet container </td>
              </tr>
          </table>
          <table class="form" cellspacing="0" cellpading="0">
              <div class="serviceheader">
                  Data Storage
              </div>
              <tr class="service">
                  <td class="description"> <img src="images/mysql.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="galera" /> mysql</td>
                  <td class="info"> MySQL-5.5 database with Galera extensions </td>
              </tr>
              <!--tr class="service">
                  <td class="description"> <img src="images/scalaris.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="scalaris" /> scalarix</td>
                  <td class="info"> Scalaris-0.7 in-memory key-value store </td>
              </tr-->
              <tr class="service">
                  <td class="description"> <img src="images/xtreemfs.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="xtreemfs" /> xtreemfs</td>
                  <td class="info"> XtreemFS-1.5 distributed file system </td>
              </tr>
          </table>
          <!--table class="form" cellspacing="0" cellpading="0">
              <div class="serviceheader">
                  High-performance computing
              </div>
              <tr class="service">
                  <td class="description"> <img src="images/hadoop.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="hadoop" /> map-reduce</td>
                  <td class="info"> Hadoop MapReduce cluster </td>
              </tr>
              <tr class="service">
                  <td class="description"> <img src="images/taskfarm.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="taskfarm" /> task farm</td>
                  <td class="info"> Service for running bags of tasks </td>
              </tr>
              <tr class="service">
                  <td class="description"> <img src="images/htc.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="htc" /> HTC </td>
                  <td class="info"> High Throughput Computing Service </td>
              </tr> 
          </table-->
          <table class="form" cellspacing="0" cellpading="0">
              <div class="serviceheader">
                  Miscellaneous
              </div>
              <!--tr class="service">
                  <td class="description"> <img src="images/selenium.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="selenium" /> selenium</td>
                  <td class="info"> Selenium functional testing service </td>
              </tr-->
              <tr class="service">
                  <td class="description"> <img src="images/generic.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="generic" /> generic</td>
                  <td class="info"> Generic service </td>
              </tr>
<!--
              <tr class="service">
                  <td class="description"> <img src="images/cds.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="cds" /> content delivery</td>
                  <td class="info"> Content-delivery service for offloading static content </td>
              </tr>
-->
<!--
              <tr class="service">
                  <td class="description"> <img src="images/htcondor.png" height="32" /></td>
                  <td class="radio"><input type="radio" name="type" value="htcondor" /> HTCondor </td>
                  <td class="info"> High Throughput Computing: Condor Pool Service </td>
              </tr> 
-->
<!--    BLUE_PRINT_INSERT    do not remove this line: it is a placeholder for installing new services -->
          </table>
          <table class="form" cellspacing="0" cellpading="0">

              <tr>
                  <td colspan="2">&nbsp;</td>
              </tr>
              <tr>
                  <td class="description">cloud provider</td>
                  <td class="input">
                  <?php
                       $clouds = json_decode(HTTPS::get(Conf::DIRECTOR . '/available_clouds'));
                       
                       foreach($clouds as $cloud){
                           if ($cloud === 'default')
                            $checked = 'checked';
                           else
                            $checked = '';
                           echo '<input type="radio"' . $checked . ' name="available_clouds" value="'.$cloud.'"/>'.$cloud.'<br/>';
                       }?>
                  </td>
              </tr>
          </table>
          <div class="createWrap">
            <a id="create" class="button" href="javascript: void(0);">
                  <img src="images/service-plus.png" style="vertical-align: top;"/> add service
              </a>
              <div class="clear"></div>
        </div>
      </div>
    <?php echo $page->renderFooter(); ?>
    <script type="text/javascript" src="js/servicepage.js"></script>
    <script type="text/javascript" src="js/create.js"></script>
  </body>
</html>
