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

    private function getCurrentExecLimit($conf) {
        if ($conf === null || !isset($conf->phpconf->max_execution_time)) {
            // default value
            return 30;
        }
        return intval($conf->phpconf->max_execution_time);
    }

    public function renderExecTimeOptions($conf) {
        static $options = array(30, 60, 120, 180, 240, 300);
        $selected = $this->getCurrentExecLimit($conf);
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

    private function getCurrentMemLimit($conf) {
        if ($conf === null || !isset($conf->phpconf->memory_limit)) {
            // default value
            return '128M';
        }
        return $conf->phpconf->memory_limit;
    }

    public function renderMemLimitOptions($conf) {
        static $options = array('64M', '128M', '256M', '512M');
        $selected = $this->getCurrentMemLimit($conf);
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

    private function getCurrentUploadMaxSize($conf) {
        if ($conf === null || !isset($conf->phpconf->upload_max_filesize)) {
            // default value
            return '2M';
        }
        return $conf->phpconf->upload_max_filesize;
    }

    public function renderUploadMaxSizeOptions($conf) {
        static $options = array('2M', '8M', '16M', '32M', '64M', '128M');
        $selected = $this->getCurrentUploadMaxSize($conf);
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

    private function getCurrentPostMaxSize($conf) {
        if ($conf === null || !isset($conf->phpconf->post_max_size)) {
            // default value
            return '8M';
        }
        return $conf->phpconf->post_max_size;
    }

    public function renderPostMaxSizeOptions($conf) {
        static $options = array('2M', '8M', '16M', '32M', '64M', '128M');
        $selected = $this->getCurrentPostMaxSize($conf);
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

    private function getCurrentDisableFunctions($conf) {
        if ($conf === null || !isset($conf->phpconf->disable_functions)) {
            // default value
            return 'pcntl_alarm,pcntl_fork,pcntl_waitpid,pcntl_wait,pcntl_wifexited,pcntl_wifstopped,pcntl_wifsignaled,pcntl_wexitstatus,pcntl_wtermsig,pcntl_wstopsig,pcntl_signal,pcntl_signal_dispatch,pcntl_get_last_error,pcntl_strerror,pcntl_sigprocmask,pcntl_sigwaitinfo,pcntl_sigtimedwait,pcntl_exec,pcntl_getpriority,pcntl_setpriority';
        }
        return $conf->phpconf->disable_functions;
    }

    public function renderDisableFunctionsField($conf) {
        $value = $this->getCurrentDisableFunctions($conf);
        $html = '<input type="text" size="50" id="conf-disablefunctions" value="'.$value.'" />';
        return $html;
    }

    private function getDebugModeStatus($conf) {
        if ($conf === null || !isset($conf->phpconf->display_errors)) {
            // default value
            return 'Off';
        }
        return $conf->phpconf->display_errors;
    }

    public function renderDebugModeOptions($conf) {
        static $options = array('On', 'Off');
        $selected = $this->getDebugModeStatus($conf);
        $html = '<select id="conf-debugmode">';
        foreach ($options as $option) {
            $selectedField = $selected == $option ?
                'selected="selected"' : '';
            $html .= '<option value="'.$option.'" '.$selectedField.'>'
                .$option.'</option>';
        }
        $html .= '</select>';
        return $html;
    }

    private function getCurrentCooldownTime($conf) {
        if ($conf === null || !isset($conf->phpconf->cool_down)) {
            // default value
            return '10';
        }
        return $conf->phpconf->cool_down;
    }

    public function renderCooldownTimeOptions($conf) {
        static $options = array('5','10','15');
        $selected = $this->getCurrentCooldownTime($conf);
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

    private function getCurrentResponseTime($conf) {
        if ($conf === null || !isset($conf->phpconf->response_time)) {
            // default value
            return '700';
        }
        return $conf->phpconf->response_time;
    }

    public function renderResponseTimeField($conf) {
        $value = $this->getCurrentResponseTime($conf);
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
        return '<select name="strategy" id="strategy"><option value="low">Standard</option><option value="medium_low">Medium</option><option value="medium">High</option><option value="optimal">Very high</option><option value="high">Insane</option></select>';
    }

    public function renderAutoscalingSettingsSection($conf) {
        return
        '<div class="form-section">'
            .'<div class="form-header">'
                .'<div class="title" align="left">Autoscaling settings</div>'
                .'<div class="clear" align="right">'.$this->renderAutoscalingStatus()
                .'</div>'
            .'</div>'
            .'<table class="form settings-form">'
                .$this->renderSettingsRow('Maximum acceptable response time',
                    $this->renderResponseTimeField($conf))
                .$this->renderSettingsRow('Cool down time',
                    $this->renderCooldownTimeOptions($conf))
                .$this->renderSettingsRow('Autoscaling aggressiveness',
                    $this->renderAutoscalingSlider())
            .'</table>'
        .'</div>';
    }

    public function renderSettingsSection($conf) {
        return
        '<div class="form-section">'
            .'<div class="form-header">'
                .'<div class="title">Settings</div>'
                .'<div class="clear"></div>'
            .'</div>'
            .'<table class="form settings-form">'
                //.$this->renderSettingsRow('Software Version',
                //    $this->renderSwVersionInput())
                .$this->renderSettingsRow('Maximum script execution time',
                    $this->renderExecTimeOptions($conf))
                .$this->renderSettingsRow('Memory limit',
                    $this->renderMemLimitOptions($conf))
                .$this->renderSettingsRow('Maximum allowed size for uploaded files',
                    $this->renderUploadMaxSizeOptions($conf))
                .$this->renderSettingsRow('Maximum size of POST data',
                    $this->renderPostMaxSizeOptions($conf))
                .$this->renderSettingsRow('Disabled PHP functions',
                    $this->renderDisableFunctionsField($conf))
                .$this->renderSettingsRow('Debug mode',
                    $this->renderDebugModeOptions($conf))
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
        $conf = $this->service->getConfiguration();
        return $this->renderInstancesSection()
            .$this->renderCdsSection()
            .$this->renderCodeSection()
            // .$this->renderAutoscalingSettingsSection($conf)
            .$this->renderSettingsSection($conf);
    }
}
