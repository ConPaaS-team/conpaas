<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class Instance {

	protected $info;

	public function __construct($info) {
		$this->info = $info;
	}

    protected function renderAgentLogs() {
        $linkAgentLogs = LinkUI('agent log',
            'viewlog.php?aid='.$_SESSION['aid']
            .'&sid='.$this->info['sid']
            .'&agentId='.$this->info['id']
        )->setExternal(true);
        $html = '<div class="right agent-logs">'
					.$linkAgentLogs
				.'</div>';
        return $html;
    }

	public function render() {
		return
		'<div class="instance dualbox">'
			.'<div class="left">'
				.'<i class="title">Instance '.$this->info['id'].'</i>'
				.$this->renderCapabs()
				.'<div class="cloud-name" title="cloud provider">'
					.$this->info['cloud']
				.'</div>'
			.'</div>'
			.'<div class="right agent-ip-address">'
				.'<i class="address">'.$this->info['ip'].'</i>'
			.'</div>'
			.$this->renderAgentLogs()
			.'<div class="clear"></div>'
		.'</div>';
	}

	public function renderInCluster() {
		return
		'<div class="instance dualbox">'
			.'<div class="left">'
				.'<i class="title">Instance '.$this->info['id'].'</i>'
				.'<i class="cloud-name" title="cloud provider">'
					.$this->info['cloud']
				.'</i>'
			.'</div>'
			.'<div class="right agent-ip-address">'
				.'<i class="address">'.$this->info['ip'].'</i>'
			.'</div>'
			.$this->renderAgentLogs()
			.'<div class="clear"></div>'
		.'</div>';
	}

	public function getSize() {
		return 1;
	}

}

?>
