<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class PhpPage extends HostingPage {

	private function renderSettingsRow($description, $input) {
		return
			'<tr>'
				.'<td class="description">'.$description.'</td>'
				.'<td class="input">'.$input.'</td>'
			.'</tr>';
	}

	private function renderSwVersionInput() {
		return
		'<select onchange="confirm(\'Are you sure you want to change the '
			.' software version?\')">'
	  		.'<option>5.3</option>'
	  	.'</select>';
	}

	private function getCurrentExecLimit() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->max_execution_time)) {
			// default value
			return 30;
		}
		return intval($conf->phpconf->max_execution_time);
	}

	public function renderExecTimeOptions() {
		static $options = array(30, 60, 120, 180, 240, 300);
		$selected = $this->getCurrentExecLimit();
		$html = '<select id="conf-maxexec">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.' seconds</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentMemLimit() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->memory_limit)) {
			// default value
			return '128M';
		}
		return $conf->phpconf->memory_limit;
	}

	public function renderMemLimitOptions() {
		static $options = array('64M', '128M', '256M');
		$selected = $this->getCurrentMemLimit();
		$html = '<select id="conf-memlim">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.'</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentUploadMaxSize() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->upload_max_filesize)) {
			// default value
			return '2M';
		}
		return $conf->phpconf->upload_max_filesize;
	}

	public function renderUploadMaxSizeOptions() {
		static $options = array('2M', '16M', '256M', '1024M', '4096M');
		$selected = $this->getCurrentUploadMaxSize();
		$html = '<select id="conf-uploadmaxsize">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.'</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentPostMaxSize() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->post_max_size)) {
			// default value
			return '4M';
		}
		return $conf->phpconf->post_max_size;
	}

	public function renderPostMaxSizeOptions() {
		static $options = array('4M', '20M', '300M', '1200M', '4192M');
		$selected = $this->getCurrentPostMaxSize();
		$html = '<select id="conf-postmaxsize">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.'</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentDisableFunctions() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->disable_functions)) {
			// default value
			return 'disk_free_space, diskfreespace, dl, exec, fsockopen, highlight_file, ini_alter, ini_restore, mail, openlog, parse_ini_file, passthru, phpinfo, popen, proc_close, proc_get_status, proc_nice, proc_open, proc_terminate, set_time_limit, shell_exec, show_source, symlink, system';
		}
		return $conf->phpconf->disable_functions;
	}

	public function renderDisableFunctionsField() {
        $value = $this->getCurrentDisableFunctions();
        $html = '<input type="text" size="50" id="conf-disablefunctions" value="'.$value.'" />';
        return $html;
    }
    
    private function getCurrentCooldownTime() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->cool_down)) {
			// default value
			return '10';
		}
		return $conf->phpconf->cool_down;
	}
    
    public function renderCooldownTimeOptions() {
		static $options = array('5','10','15');
		$selected = $this->getCurrentCooldownTime();
		$html = '<select id="conf-cool_down">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.' minutes</option>';
		}
		$html .= ' </select>';
		return $html;
	}
	
	private function getCurrentResponseTime() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->response_time)) {
			// default value
			return '700';
		}
		return $conf->phpconf->response_time;
	}
	
	public function renderResponseTimeField() {
        $value = $this->getCurrentResponseTime();
        $html = '<input type="text" size="4" id="conf-response_time" value="'.$value.'" /> milliseconds';
        return $html;
    }

	public function renderAutoscalingStatus() {
		if ($this->service->isAutoscalingON()) {
			return '<label class="checkbox toggle candy" onclick="" style="width: 100px"> <input id="scaling" type="checkbox" checked/><p><span>On</span><span>Off</span></p><a class="slide-button"></a></label>';
				
		}
		return '<label class="checkbox toggle candy" onclick="" style="width: 100px"> <input id="scaling" type="checkbox" /><p><span>On</span><span>Off</span></p><a class="slide-button"></a></label>';
	}
	
	public function renderAutoscalingSlider() {
		return '<select name="strategy" id="strategy"><option value="low">Standard</option><option value="medium_low">Good</option><option value="medium">Well-Adjusted</option><option value="optimal">Optimal</option><option value="high">Excellent</option></select>';
	}
	
	public function renderAutoscalingSettingsSection() {
		return
		'<div class="form-section">'
			.'<div class="form-header">'
				.'<div class="title" align="left">Autoscaling settings</div>'
				.'<div class="clear" align="right">'.$this->renderAutoscalingStatus()
				.'</div>'
			.'</div>'
			.'<table class="form settings-form">'
				.$this->renderSettingsRow('Response time',
					$this->renderResponseTimeField())
				.$this->renderSettingsRow('Cool down time',
					$this->renderCooldownTimeOptions())
				.$this->renderSettingsRow('QoS autoscaling (performance/cost)',
					$this->renderAutoscalingSlider())
			.'</table>'
		.'</div>';
	}
	
	public function renderSettingsSection() {
		return
		'<div class="form-section">'
			.'<div class="form-header">'
				.'<div class="title">Settings</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<table class="form settings-form">'
				//.$this->renderSettingsRow('Software Version',
				//	$this->renderSwVersionInput())
				.$this->renderSettingsRow('Maximum script execution time',
					$this->renderExecTimeOptions())
				.$this->renderSettingsRow('Memory limit',
					$this->renderMemLimitOptions())
				.$this->renderSettingsRow('Maximum allowed size for uploaded files',
					$this->renderUploadMaxSizeOptions())
				.$this->renderSettingsRow('Maximum size of POST data',
					$this->renderPostMaxSizeOptions())
				.$this->renderSettingsRow('Disabled PHP functions',
					$this->renderDisableFunctionsField())
				.'<tr><td class="description"></td>'
					.'<td class="input actions">'
					.'<input id="saveconf" type="button" disabled="disabled" '
						.'value="save" />'
					 .'<i class="positive invisible">Submitted successfully</i>'
					.'</td>'
				.'</tr>'
			.'</table>'
		.'</div>';
	}

	private function renderCdsForm() {
		if ($this->service->isCdnEnabled()) {
			return
			'Content delivery is <b>ON</b> using '
			.'<b>'.$this->service->getCds()->getName().'</b>. '
			.'You should be able to get the following variables into your application:'
			.'<div class="code">'
				.'<b class="line" title="url prefix for offloaded content">'
					.'$_SERVER[\'CDN_URL_PREFIX\']'
				.'</b>'
				.'<b class="line" title="country of the remote address">'
					.'$_SERVER[\'GEOIP_COUNTRY_CODE\']'
				.'</b>'
			.'</div>';
		}
		$cdsServices = $this->service->getAvailableCds($this->getUID());
		$options = '';
		$subscribeButton = InputButton('subscribe')->setId('cds_subscribe');
		if (count($cdsServices) > 0) {
			foreach ($cdsServices as $cds) {
				$options .= '<option value="'.$cds->getSID().'">'
					.$cds->getName().'</option>';
			}
		} else {
			$options = '<option>No available CDS</option>';
			$subscribeButton->setDisabled(true);
		}
		// we cannot subscribe to a CDS if we are not running, because we don't
		// have an origin address yet
		if (!$this->service->isRunning()) {
			$subscribeButton
				->setDisabled(true)
				->setTitle('the service must be running');
		}
		return
		'Content delivery is <b>OFF</b>. To be able to offload static content '
		.'you may want to subscribe to one of the available CDN services.'
		.'<div class="subscribe-form">'
			.'<select id="cds">'.$options.'</select> '
			.$subscribeButton.' '
			.'<img id="subscribe-loading" class="invisible" src="images/icon_loading.gif" />'
		.'</div>';
	}

	public function renderCdsStatus() {
		if ($this->service->isCdnEnabled()) {
			return
			InputButton('unsubscribe')->setId('cds_unsubscribe')
			.'<img class="led" src="images/ledgreen.png" '
				.'title="Content Delivery is ON" /> ';
		}
		return '<img class="led" src="images/ledorange.png" '
			.'title="Content Delivery is OFF"/>';
	}

	public function renderCdsSection() {
		return '';
        /*
		'<div class="form-section">'
			.'<div class="form-header">'
				.''
				.'<div class="title">'
					.'<img src="images/cds.png" width="23"/><i>Content Delivery</i>'
				.'</div>'
				.'<div class="access-box">'
					.$this->renderCdsStatus()
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<div class="cds-subscribe">'
				.$this->renderCdsForm()
			.'</div>'
		.'</div>';
       */
	}

	public function renderContent() {
		return $this->renderInstancesSection()
			.$this->renderCdsSection()
			.$this->renderCodeSection()
			.$this->renderAutoscalingSettingsSection()
			.$this->renderSettingsSection();
	}
}
