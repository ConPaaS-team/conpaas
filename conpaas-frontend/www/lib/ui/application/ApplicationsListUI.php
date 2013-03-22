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

class ApplicationsListUI {

	private $applications;

	public function __construct(array $applications) {
		$this->applications = $applications;
	}

	public function addApplication(Application $application) {
		$this->applications[] = $application;
		return $this;
	}

	public function isEmpty() {
		return count($this->applications) == 0;
	}

	private function renderItems() {
		$html = '';
		for ($i = 0; $i < count($this->applications); $i++) {
			try {
				$applicationUI = new DashboardApplicationUI($this->applications[$i]);
				if ($i == count($this->applications) - 1) {
					$applicationUI->setLast();
				}
				$html .= $applicationUI->__toString();
			} catch (Exception $e) {
				// just skip the bad behaving service and report the exception
				dlog('Exception trying to render the dashboard application UI:'
					.' sid: '.$this->applications[$i]->getAID()
					.' error: '.$e->getMessage());
			}
		}
		return $html;
	}

	public function needsRefresh() {
		foreach ($this->applications as $application) {
			if ($application->needsPolling()) {
				return true;
			}
		}
		return false;
	}

	public function render() {
		if (count($this->applications) == 0) {
			return
			'<div class="box infobox">'
				.'You have no applications in the dashboard. '
				.'Go ahead and <a href="create.php">create a new application</a>.'
			.'</div>';
		}
		return
		'<div class="services">'.
			'<table class="slist" cellpadding="0" cellspacing="1">'.
				$this->renderItems().
			'</table>'.
		'</div>';
	}

	public function toArray() {
		$descr = array();
		foreach ($this->applications as $application) {
			$descr []= $application->toArray();
		}
		return $descr;
	}
}
