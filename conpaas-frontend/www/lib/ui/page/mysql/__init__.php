<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('ui');
require_module('ui/page');

class MySQLPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('https://www.google.com/jsapi');
        // $this->addJS('http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js');
		$this->addJS('js/jquery.form.js');
		$this->addJS('js/mysql.js');
		
               
		if ($this->service->isRunning() && $this->needsPasswordReset()) {
			$this->addMessage($this->passwordResetMessage(),
				MessageBox::WARNING);
		}
	}

	/*
	 * overrides ServicePage.getTypeImage()
	 */
	protected function getTypeImage() {
		return 'mysql.png';
	}

	private function passwordResetMessage() {
		return
		'Before using this service you must first '
		.'<a id="warningResetPasswd" href="javascript: void(0);">'
			.'reset the database password'
		.'</a>'
		.', otherwise you will not be able to access it.';
	}

	public function needsPasswordReset() {
		return $this->service->needsPasswordReset();
	}

	protected function renderApplicationAccess() {
		return '';
	}

	protected function renderInstanceActions() {
		$html = '';
                static $roles = array('mysql', 'glb');
                foreach ($roles as $role) {
                        $html .= EditableTag()
                                ->setColor(Role::getColor($role))
                                ->setID($role)
                                ->setValue('0')
                                ->setText(Role::getText($role))
                                ->setTooltip(Role::getInfo($role));
                }
                return $html;
	}

	private function renderFormRow($name, $details) {
		return
			'<div class="left-stack name">'.$name.'</div>'
			.'<div class="left-stack details">'.$details.'</div>'
			.'<div class="clear"></div>';
	}

	private function renderPasswordInput() {
		$invisible = $this->needsPasswordReset() ? '' : 'invisible';
		return
			'<div id="passwordForm" class="'.$invisible.'">'
				.'<div class="left-stack name">new password</div>'
				.'<div class="left-stack details">'
					.'<input id="passwd" type="password" />'
					.'<b class="hint"> at least 8 characters</b>'
				.'</div>'
				.'<div class="clear"></div>'
				.'<div class="left-stack name">retype password</div>'
				.'<div class="left-stack details">'
					.'<input id="passwdRe" type="password" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderPasswordResetIndicator() {
		if (!$this->needsPasswordReset()) {
			return '';
		}
		return
		'<div class="selectHint">'
			.'<img src="images/warning.png" /> please reset your password '
			.'<img width="12px" src="images/lookdown.png" />'
		.'</div>';
	}

	private function renderPasswordReset() {
		$invisible = $this->needsPasswordReset() ? '' : 'invisible';
		return $this->renderPasswordResetIndicator()
			.$this->renderPasswordInput()
			.'<div id="resetPasswordForm" class="'.$invisible.'">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="resetPassword" type="button" '
						.' value="reset password" />'
					.'<i id="resetStatus" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderCommand() {
		$users = $this->service->getUsers();
		$master_addr = $this->service->getMasterAddr();
		$cmd = 'mysql --host='.$master_addr['ip'].' --port='.$master_addr['port'].' -u '.$users[0].' -p';
		return '<input class="command" type="text" readonly="readonly" '
			.' value="'.$cmd.'" title="shell command"/>'
			.'<b class="hint"> Click on command to Copy it</b>';
	}

	private function renderUsers() {
		$users = $this->service->getUsers();
		return $this->renderFormRow('user',
			'<span id="user">'.$users[0].'</span>');
	}

	public function renderAccessForm() {
		return
		'<div class="form-section mysql-access">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/key.png"/>MySQL Access'
				.'</div>'
				.'<div class="access-box">'
					.'<a id="showResetPasswd" href="javascript: void(0);">'
						.'reset password'
					.'</a>'
					//.' &middot; <a href="javascript: void(0);">add user</a>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderFormRow('server address',
				$this->service->getAccessLocation())
			.$this->renderUsers()
			.$this->renderFormRow(
				'<img src="images/terminal.png" title="shell command" />',
				$this->renderCommand())
			.$this->renderPasswordReset()
		.'</div>';
	}

	public function renderLoadSection() {
		return
		'<div class="form-section mysql-load">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/dbload.png"/>Load database from file'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<form id="loadform" action="ajax/dbload.php" '
				.'enctype="multipart/form-data">'
				.'<input id="dbfile" type="file" name="dbfile" />'
				.'<input id="loadfile" type="button" value="Load file" '
					.'disabled="disabled" />'
				.'<input type="hidden" name="sid" '
					.' value="'.$this->service->getSID().'" />'
				.'<img class="loading invisible" '
					.'src="images/icon_loading.gif"/>'
				.'<i class="positive invisible">File loaded successfully</i>'
				.'<i class="error invisible">Error loading file</i>'
			.'</form>'
		.'</div>';
	}

	public function renderPerformanceForm() {
        return  '<div class="form-section mysql-access">'
                        .'<div class="form-header">'
                                .'<div class="title" style="width:100%">'
                                        // .'<table style="width:100%"><tr><td><img src="images/Performance.png"/>Performance Monitor</td><td align="right"><span id="showStats" style="cursor:pointer">Show</span></td></tr></table> '
                  				.'<img src="images/Performance.png"/>Performance Monitor <div class="access-box"><a id="showStats" href="javascript: void(0);">show</a></div>'
                                .'</div>'
                                .'<div class="clear"></div>'
                        .'</div>'
                        .'<div id="monitor_div" style="display:none; padding:10px">'
                        .''
			.'<table class="st_table" id="tableID">
  			<thead>
    			<tr>
      			<td>Hostname</td>
      			<td>CPU<br>Usage</td>
      			<td>Memory<br>Free</td>
      			<td>Disk<br>Free</td>
      			<td>Incoming<br>Packets</td>
			<td>Outgoing<br>Packets</td>
			<td>Incoming<br>KBytes</td>
			<td>Outgoing<br>KBytes</td>
			<!--<td>Delete</td>-->
    			</tr>
  			</thead>
  			<tbody>
  			</tbody>
			
			</table>'
			.'<div id="stats_div" style="width: 780px; height: 400px;"></div>'
			.'<div id="chart_div" style="width: 780px; height: 450px;"></div>'
			.'</div></div>';
        }
	
	public function renderContent() {
		$html = $this->renderInstancesSection();
		if ($this->service->isRunning()) {
			$html .= $this->renderAccessForm()
				.$this->renderLoadSection()
				.$this->renderPerformanceForm();
		}
		return $html;
	}
}
?>
