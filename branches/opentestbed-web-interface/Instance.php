<?php 

class Instance {
	
	private $info;
	
	public function __construct($info) {
		$this->info = $info;
	}
	
	private function renderCapabs() {
		$html = '';
		if ($this->info['isRunningProxy']) {
			$html .= '<div class="tag orange">proxy</div>';
		}
		if ($this->info['isRunningWeb']) {
			$html .= '<div class="tag blue">web</div>';
		}
		if ($this->info['isRunningBackend']) {
			$html .= '<div class="tag purple">' . $this->info['service_type'] . '</div>';
		}
		return $html;
	}
	
	public function render() {
		return
		'<div class="instance dualbox">'
			.'<div class="left">'
				.'<i class="title">Instance '.$this->info['id'].'</i>'
				.$this->renderCapabs()
				.'<div class="brief">running</div>'
			.'</div>'
			.'<div class="right">'
				.'<i class="address">'.$this->info['ip'].'</i>'
			.'</div>'
			.'<div class="clear"></div>'
		.'</div>';
	}
	
	public function renderInCluster() {
		return
		'<div class="instance dualbox">'
			.'<div class="left">'
				.'<i class="title">Instance '.$this->info['id'].'</i>'
				.'<i class="timestamp">running for 6 hours</i>'
			.'</div>'
			.'<div class="right">'
				.'<i class="address">'.$this->info['ip'].'</i>'
			.'</div>'
			.'<div class="clear"></div>'
		.'</div>';
	}
	
	public function getSize() {
		return 1;
	}
}

?>
