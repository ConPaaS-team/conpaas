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
    <?php echo $page->renderTitle(' - Application'); ?>
    <?php echo $page->renderIcon(); ?>
    <?php echo $page->renderHeaderCSS(); ?>
    <?php echo $page->generateJSGetParams(); ?>
    
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">
	<?php echo $page->renderHeader(); ?>
	<div class="pagecontent">
		<?php echo $page->renderTopMenu(); ?>
		<div class="pageheader">
			<?php echo $page->renderPageHeader(); ?>
		</div>
		
		
		<table border="0" style="width:100%"><tr><td style="width:40px">
		<!-- <a id="showuploaddiv" class="button" href="#" style="border-radius: 30px; display:none; margin-left: 10px; position:absolute; z-index:20"><img style="margin:0px; width: 16px" src="images/upload.png"></img></a> -->
		<img id="showuploaddiv" style="margin:5px; width: 35px; display:none; position:absolute; z-index:20" src="images/upload1.png"></img>
		<div style="height:20px"></div>
		</td><td>
		<div id="uploaddiv" style="text-align:center">
			<!--div style="background:red; float: right;height: 105px; width:12px; vertical-align: middle; display: table-cell;">&lt;</div-->
			
			<table style="width:100%" border="0"><tr><td> 
			<input id="manfile" name="manfile" type="file" style="display:none">
			<input id="appfile" name="appfile" type="file" style="display:none">
			
			<a id="upmanfile" class="button small file" href="#"><!--img src="images/service-plus.png"></img-->&nbsp;&nbsp;Upload manifest...&nbsp;</a>
			<div id="manfilename" class="filename"></div>
			
			<br/><br/>
			
			<a id="upappfile" class="button small file" href="#"><!--img src="images/service-plus.png"></img-->Upload application...</a>
			<div id="appfilename" class="filename"></div>
			
			<br/><br/><br/>

			<a id="uploadManifest" class="button  " href="#">Submit</a>
			</td>
			<td id="hideuploaddiv" class="hide" valign="top" style="">[x]</td>
			</tr></table>

			<!--table border="1" cellpadding="0" style="width:100%">          
             <tr><td align="center"><a id="upmanfile" class="button small file" href="#"><img src="images/service-plus.png"></img>Upload manifest...</a></td><td style="text-align:right"><div id="manfilename"></div></td></tr>  
             <tr><td align="center"><a id="upappfile" class="button" href="#"><img src="images/service-plus.png"></img>Upload application...</a></td><td style="text-align:right"><div id="appfilename"></div></td></tr>
             </table-->
             
        </div>
		</td>
		</tr>
		</table>

		<div id="servicesWrapper" style="padding:10px"></div>
		
		<div id="profilediv" style="display:none ">

			<hr/>
			<div style="padding-top:10px; padding-bottom:10px; text-align:center">
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
	            <input id="profilefile" name="profilefile" type="file" style="display:none"/> 
	            <a id="upprofilefile" class="button small" href="#"><!--img src="images/service-plus.png"></img-->Upload profile...</a><div id="profilefilename" style="display:inline"></div>
	           &nbsp;&nbsp;&nbsp;&nbsp;&nbsp; or &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
				<a id="profile" class="button small" href="#"><img src="images/service-plus.png"/>Start profiling</a>
				<img id="settings" data-popup-target="#example-popup" src="images/setting.png" style="cursor:pointer; width:20px; " />
	        </div>

	        <table style="width:100%">
	        	<tr>
	        	<td valign="top"><div id="divProfileTable" style="padding: 10px;height: 200px; width:330px; /*overflow:auto; overflow-x:hidden*/"></div></td>	
	        	<td valign="top" width="500" align="right"><div id="divProfileChart" style="height:280px;width:500px; "></div><div id="failed" align="center" style="width:100%;"></div></td>	
	        	</tr>
	        	<tr>
	        	<td align="center" colspan="2"><div id="downloadProfile" style="margin-top: 10px;"></div></td>
	        	</tr>
	        </table>
		
		</div>
		<div id="slodiv" style="display:none">	

			<hr/>
			<div align="center" style="padding-left:10px; padding-right:10px; ">
			<table border="0" style="width:100%; margin-bottom:5px;"><tr align="center" style="cursor:pointer;">
			<td group="cheap" class="pre-configure" style="width:33.3%" title="Cheapest"><img group="cheap" src="images/save.png" style="width:30px" title="Cheapest" /> </td>
			<td group="balanced" class="pre-configure" style="width:33.3%" title="Balanced"><img group="balanced" src="images/balance.png" style="width:30px" title="Balanced" /></td>
			<td group="fast" class="pre-configure" style="width:33.3%" title="Fastest"><img group="fast" src="images/fast.png" style="width:30px" title="Fastest" /> </td>
			</tr></table>
			

			<table border="0" style="width:100%">
			<tr><td rowspan="2"  width="48%" valign="top">
			<table id="constraintTable" border="0">
			<tr><td >
			<div style="margin-bottom:15px" >Optimize:</div>
			</td>
			<td>
			<select id="optimizeSelect" style="margin-bottom:15px">
			  <option value="execution_time">Execution time</option>
			  <option value="cost">Cost</option>
			</select> 
			<a id="showConfiguration" class="button small" href="#divProfileTable">Show configuration</a>

			</td>
			</tr>	
			
			<tr>
			<td>
			<span>Constraints:</span>	
			</td>
			
			<td id="ccol_0" style="background:#F2F2F2">
			<select >
			  <option value="cost">Cost</option>
			  <option value="execution_time">Execution time</option>
			</select> 
			<select>
			  <option value="<">&lt;</option>
			  <option value="<=">&le;</option>
			  <option value=">">&gt;</option>
			  <option value=">=">&ge;</option>
			  <option value="==">=</option>
			</select> 
			<input type="text" style="width:50px; text-align:center" value="0.0" />
			<!--img src="images/remove.png"/-->
			</td>			
			</tr>
			<tr><td></td><td align="center" style="background:#F2F2F2"><img id="addConstraints" src="images/create.png" style="cursor:pointer;" /></td></tr>
			</table></td>
			<td height="65" align="center">
				<table border="0" style="width:100%; /*border:1px solid*/ " class="predictionsTab">
					<tr><td colspan="4" align="center" style="background:#F2F2F2"><strong>Selected configuration</strong></td></tr>
					<tr><td colspan="4" align="center"><span id="selectedConfig">-</span></td></tr>
					<tr><td></td><td align="center" width="100" style="background:#F2F2F2"><strong>Time(min)</strong></td><td align="center" width="100" style="background:#F2F2F2"><strong>Cost(&euro;)</strong></td><td align="center" width="100" style="background:#F2F2F2"><strong>&epsilon;(%)</strong></td></tr>
					<tr><td width="70" style="background:#F2F2F2"><strong>Estimated</strong></td><td align="center"><span id="esExecTime">-</span></td><td align="center"><span id="esCost">-</span></td><td align="center" rowspan="2"><span id="absError">-</span></td></tr>
					<tr><td style="background:#F2F2F2"><strong>Actual</strong></td><td align="center"><span id="acExecTime">-</span></td><td align="center"><span id="acCost">-</span></td></tr>
				</table>

			</td></tr>
			<tr><td valign="bottom">
			<a id="executeSlo" style="float:right; margin-top: 20px;" class="button"  href="#"> <img  src="images/play.png"/>Execute</a>
			</td>
			</tr></table>

			<!-- <input id="slofile" name="slofile" type="file" style="display:none"> 
			<table border="0" style="width:100%">
			<tr><td><div id="predictionDiv" class="prediction" >
				Selected configuration: <span>-</span> <br/>
				Estimated execution time: <span>-</span> &nbsp;&nbsp;&nbsp; Estimated cost: <span>-</span>
			</div></td><td></td></tr>
			<tr>
				<td rowspan="3" valign="top" ><textarea id="txtSlo"  style="width:600px; height:250px; background-color:#fffdf6; border: 1px solid"></textarea> </td>
				<td valign="top" align="right" style="height:40px; padding-top:10px">
					<a id="upslofile" class="button small" href="#divProfileTable">Upload SLO...</a>
				</td>
			</tr>
			<tr><td valign="top" align="right"><a id="showConfiguration" class="button small" href="#divProfileTable">Show configuration</a></td></tr>
			<tr><td valign="bottom" align="right" style="padding-bottom:10px"><a id="executeSlo" class="button" href="#"><img style="margin-top:-3px" src="images/play.png"/>Execute</a></td></tr>
			 </table>-->
			


			</div> 
		</div>
		<!--?php echo $page->renderContent(); ?-->

		
	</div>

	<div id="example-popup" class="popup">
    <div align="center" class="popup-body">	

        <div align="center" class="popup-content">
        <p>if you see this, something is definitely wrong</p>    	
        </div>

        
        <a href="#" class="button popup-exit">OK</a> 
    </div>
	</div>
	<div class="popup-overlay"></div>


	<?php echo $page->renderFooter(); ?>
	<?php echo $page->renderJSLoad(); ?>
  </body>
</html>