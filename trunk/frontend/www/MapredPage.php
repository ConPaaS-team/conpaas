<?php 

class MapredPage {
	
	static $states = array(
		'INIT' => false,
		'RUNNING' => false,
		'PROLOGUE' => true,
		'EPILOGUE' => true,
		'STOPPED' => false 
	);

	private $managerAddress;
	private $conf = null;
	
	public function __construct($data) {
		$this->managerAddress = $data['manager'];
	}
	
	public function is_transient($state) {
		return 
			!array_key_exists($state, self::$states) ||
			(self::$states[$state] == true);
	}
	
	public function getUploadURL() {
		return $this->managerAddress;
	}
	
	public function fetchState() {
		return 'RUNNING';
	}
	
	public function renderActions($state) {
		$startButton = InputButton('start')
			->setId('start');
		$stopButton = InputButton('stop')
			->setId('stop');
		$terminateButton = InputButton('terminate')
			->setDisabled(true);
		
		switch ($state) {
			case 'INIT':
				$stopButton->setVisible(false);
				$terminateButton->setVisible(false);
				break;
			case 'RUNNING':
				$startButton->setVisible(false);
				$terminateButton->setVisible(false);
				break;
			case 'STOPPED':
				$stopButton->setVisible(false);
				break;
			default:
		}
		
		return $startButton.' '.$stopButton.' '.$terminateButton;
	}

	public function renderStateClass($state) {
		switch ($state) {
			case 'INIT':
			case 'RUNNING':
				return 'active';
			case 'STOPPED':
				return 'stopped';
			default:
				return '';
		}
	}
		
}
?> 