<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



require_module('service');

function StatusLed(Service $service) {
	return new StatusLed($service);
}

class StatusLed {

	private $service;

	public function __construct(Service $service) {
		$this->service = $service;
	}

	private function getImage() {
		$state = $this->service->getState();
		if (!$this->service->isReachable()) {
			if ($state == Service::STATE_INIT ||
			    $state == Service::STATE_PREINIT) {
			    	return 'images/ledlightblue.png';
			    }
			return 'images/ledorange.png';
		}
		/* for reachable case */
		switch ($state) {
			case Service::STATE_INIT:
				return 'images/ledlightblue.png';
			case Service::STATE_RUNNING:
			case Service::STATE_ADAPTING:
			case Service::STATE_PROLOGUE:
			case Service::STATE_EPILOGUE:
				return 'images/ledgreen.png';
			case Service::STATE_STOPPED:
				return 'images/ledgray.png';
			case Service::STATE_ERROR:
				return 'images/ledred.png';
			default:
				return 'images/ledred.png';
		}
	}

	public function __toString() {
		return '<img class="led" title="'.$this->service->getStatusText().'" '
			.' src="'.$this->getImage().'" />';
	}
}
