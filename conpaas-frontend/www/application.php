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
	$_SESSION['aid'] = 0;
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
		
		
		
		
		<div style="text-align:center">
			
			<input id="manfile" name="manfile" type="file" style="display:none">
			<input id="appfile" name="appfile" type="file" style="display:none">
			
			<a id="upmanfile" class="button small file" href="#"><!--img src="images/service-plus.png"--></img>&nbsp;&nbsp;Upload manifest...&nbsp;</a>
			<div id="manfilename" class="filename"></div>
			
			<br/><br/>
			
			<a id="upappfile" class="button small file" href="#"><!--img src="images/service-plus.png"--></img>Upload application...</a>
			<div id="appfilename" class="filename"></div>
			
			<!--table border="1" cellpadding="0" style="width:100%">          
             <tr><td align="center"><a id="upmanfile" class="button small file" href="#"><img src="images/service-plus.png"></img>Upload manifest...</a></td><td style="text-align:right"><div id="manfilename"></div></td></tr>  
             <tr><td align="center"><a id="upappfile" class="button" href="#"><img src="images/service-plus.png"></img>Upload application...</a></td><td style="text-align:right"><div id="appfilename"></div></td></tr>
             </table-->
             
        </div>
		<div id="servicesWrapper" style="padding:10px"></div>
		<hr/>
		<div style="padding-top:20px; text-align:center">
		    <!--table border="0" style="width:100%"><tr>
		    <td style="width:50%">Upload profile: <input id="profilefile" name="profilefile" type="file"> </td>
		    <td align="center" style="width:10%"></td> 
		    <td align="right" style="width:40%"><a id="profile" class="button" href="#"><img src="images/service-plus.png"></img>
  			Start profiling
  			</a></td>
			</tr></table-->
		    
		    <!--table border="1" cellpadding="0" style="width:100%">          
            <tr><td style="width:150px">Upload profile: </td><td><form id="manform" action="ajax/parseManifest.php" method="POST"><input id="profilefile" name="profilefile" type="file"></form></td></tr>  
            </table-->
            <input id="profilefile" name="profilefile" type="file" style="display:none"> 
            <a id="upprofilefile" class="button small" href="#"><!--img src="images/service-plus.png"></img-->Upload profile...</a><div id="profilefilename" style="display:inline"></div>
           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; or &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
			<a id="profile" class="button small" href="#"><img src="images/service-plus.png"></img>Start profiling</a>
        </div>
        <br/><br/>
        <table style="width:100%">
        	<tr>
        	<td valign="top"><div id="divProfileTable" style="padding: 10px;"></div></td>	
        	<td valign="top" align="right"><div id="divProfileChart" style="height:200px;width:300px; "></div></td>	
        	</tr>
        	<tr>
        	<td align="center" colspan="2"><div id="downloadProfile"></div></td>
        	</tr>
        </table>
		
		<hr/>
		<div style="padding:10px">
		<!--textarea id="txtSlo" class="codepress javascript linenumbers-on" style="width:600px; height:300px"></textarea--> 
		<input id="slofile" name="slofile" type="file" style="display:none"> 
		<table border="0" style="width:100%"><tr>
			<td rowspan="3" valign="top" ><textarea id="txtSlo"  style="width:600px; height:250px; background-color:#fffdf6; border: 1px solid"></textarea> </td>
			<td valign="top" align="right" style="height:40px; padding-top:10px">
				<a id="upslofile" class="button small" href="#"><!--img src="images/green-up.png"--></img>Upload SLO...</a>
				
			</td>
		</tr>
		<tr><td valign="top" align="right"><a id="showConfiguration" class="button small" href="#"><!--img src="images/service-plus.png"--></img>Show configuration</a></td></tr>
		<tr><td valign="bottom" align="right" style="padding-bottom:10px"><a id="showConfiguration" class="button" href="#"><img style="margin-top:-3px" src="images/play.png"></img>Execute</a></td></tr>
		</table>
		
		</div>

		<!--?php echo $page->renderContent(); ?-->

		
	</div>
	<?php echo $page->renderFooter(); ?>
	<?php echo $page->renderJSLoad(); ?>
  </body>
</html>
