<?php
/* Copyright (C) 2010-2013 by Contrail Consortium. */



class JavaPage extends HostingPage {

	public function renderContent() {
		return $this->renderInstancesSection()
			.$this->renderCodeSection();
	}
}
