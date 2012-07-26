<?php

require_module('aws-sdk');
require_module('logging');

class EC2Cloud extends Cloud {

	private $ec2;

	public function __construct() {
		$this->ec2 = new AmazonEC2();
	}

	public function getName() {
		return 'Amazon EC2';
	}

	public function getLogo() {
		return '<img class="cloud" src="images/aws.png" />';
	}

	public function getAvailableRegions() {
		$all_regions = array(
			AmazonEC2::REGION_US_E1 =>
				new Region('US', 'Northern Virginia', '',
					AmazonEC2::REGION_US_E1),
			AmazonEC2::REGION_US_W1 =>
				new Region('US', 'Northern California', '',
					AmazonEC2::REGION_US_W1),
			'us-west-2' =>
				new Region('US', 'Oregon', '', 'us-west-2'),
			'sa-east-1' =>
				new Region('BR', 'Brazil', 'South America', 'sa-east-1'),
			AmazonEC2::REGION_EU_W1 =>
				new Region('IE', 'Ireland', 'Europe', AmazonEC2::REGION_EU_W1),
			AmazonEC2::REGION_APAC_SE1 =>
				new Region('SG', 'Singapore', 'Asia Pacific',
					AmazonEC2::REGION_APAC_SE1),
			AmazonEC2::REGION_APAC_NE1 =>
				new Region('JP', 'Japan', 'Asia Pacific',
					AmazonEC2::REGION_APAC_NE1),
		);
		$response = $this->ec2->describe_regions();
		$regions = $response->body->regionInfo;
		$regions = $regions->to_array();
		$regions = $regions['item'];
		$availableRegions = array();
		foreach ($regions as $region) {
			if (isset($all_regions[$region['regionName']])) {
				$availableRegions []= $all_regions[$region['regionName']];
			}
		}
		return $availableRegions;
	}
}