<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

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
