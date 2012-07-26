<?php

class Region {

	public $country,
		$state,
		$continent,
		$id,
		$edge_locations = array();

	public function __construct($country, $state, $continent, $id) {
		$this->country = $country;
		$this->state = $state;
		$this->continent = $continent;
		$this->id = $id;
	}

	public function getFlagURL() {
		if ($this->continent == 'Europe') {
			return 'images/countries/europeanunion.png';
		}
		return 'images/countries/'.strtolower($this->country).'.png';
	}

	public function hasEdgeLocations() {
		return count($this->edge_locations) > 0;
	}

	public function __toString() {
		$html = $this->state;
		if ($this->continent) {
			$html .= ', '.$this->continent;
		}
		return $html;
	}
}