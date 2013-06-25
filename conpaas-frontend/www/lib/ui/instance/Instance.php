<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class Instance {

	protected $info;

	public function __construct($info) {
		$this->info = $info;
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
				.'<i class="timestamp">running</i>'
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
