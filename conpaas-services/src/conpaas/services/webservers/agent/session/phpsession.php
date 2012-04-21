<?php

class ScalarisException extends Exception {}
class RequestException extends ScalarisException {}
class JSONFormatException extends ScalarisException {}
class UnknownResponseException extends  ScalarisException {}

class ScalarisNotFoundException extends  ScalarisException {}
class ScalarisGetException extends  ScalarisException {}
class ScalarisPutException extends  ScalarisException {}

function _error_log($msg) {
  error_log($msg, 3, '/tmp/php.log');
}

class Scalaris {

  public function __construct() {
    $this->id = NULL;
    $this->data = NULL;
    $this->VAR_CACHE = '/var/cache/cpsagent/';
  }

  /**
   * Perform an http POST request to $this->path (supplied to open())
   * with parameters given in $params.
   *
   * @param array $params Associative array for parameters to JSON encode and send.
   */
  private function http_post($params) {
    $data = json_encode($params);
    $headers = array();
    $headers[] = 'Content-length: ' . strlen($data);
    $headers[] = 'Content-type: application/json';
    $headers[] = 'Connection: close';
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_URL, $this->path);
    curl_setopt($ch, CURLOPT_POST, TRUE);
    curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    $response = curl_exec($ch);
    if ($response == FALSE) {
      _error_log(__METHOD__ . ':' . __LINE__);
      throw new RequestException();
    }
    $json_response = json_decode($response);
    if ($json_response == NULL) {
      _error_log(__METHOD__ . ':' . __LINE__);
      throw new JSONFormatException();
    }
    return $json_response;
  }

  /**
   * Get the value to key from Scalaris.
   * Returns: value of key
   *
   * @param string $key
   * @throws ScalarisNotFoundException key not found
   * @throws ScalarisGetException unknown failure reason or http errors
   * @throws UnknownResponseException malformed response
   */
  private function scalaris_get($key) {
    $params = array();
    $params['version'] = '1.1';
    $params['id'] = 0;
    $params['method'] = 'read';
    $params['params'] = array($key);

    try {
      $response = $this->http_post($params);
    } catch(ScalarisException $e) {
      _error_log(__METHOD__ . ':' . __LINE__);
      throw new ScalarisGetException('HTTP request failed');
    }
    if (isset($response->result) && isset($response->result->status)) {
      if ($response->result->status == 'ok' && isset($response->result->value)) {
        return $response->result->value->value;
      }
      elseif ($response->result->status == 'fail' && isset($response->result->reason)) {
        if ($response->result->reason == 'not_found') {
          _error_log(__METHOD__ . ':' . __LINE__);
          throw new ScalarisNotFoundException();
        }
        else {
          _error_log(__METHOD__ . ':' . __LINE__);
          throw new ScalarisGetException('Get operation failed, reason: ' . $response->result->reason);
        }
      }
      else {
        _error_log(__METHOD__ . ':' . __LINE__);
        throw new UnknownResponseException();
      }
    }
    else {
      _error_log(__METHOD__ . ':' . __LINE__);
      throw new UnknownResponseException();
    }
  }

  /**
   * Write value to key.
   * Returns: success TRUE | False
   *
   * @param string $key
   * @param string $value
   * @throws ScalarisPutException http errors
   * @throws UnknownResponseException malformed response
   */
  public function scalaris_put($key, $value) {
    $params = array();
    $params['version'] = '1.1';
    $params['id'] = 0;
    $params['method'] = 'write';
    $params['params'] = array($key, array('type'=>'as_is', 'value'=>$value));
    try {
      $response = $this->http_post($params);
    } catch(ScalarisException $e) {
      _error_log(__METHOD__ . ':' . __LINE__);
      throw new ScalarisPutException('HTTP request failed');
    }
    if (isset($response->result) && isset($response->result->status)) {
      if ($response->result->status == 'ok') return TRUE;
      else return FALSE;
    }
    else {
      _error_log(__METHOD__ . ':' . __LINE__);
      throw new UnknownResponseException();
    }
  }

  public function open($save_path, $session_name) {
//    _error_log('XXX open: "'. $save_path . '", "' . $session_name . '"');
    $this->path = file_get_contents($this->VAR_CACHE.'fpm-scalaris.conf');
    $this->session_name = $session_name;
    return TRUE;
  }

  public function close() {
//    _error_log("XXX close:");
    return TRUE;
  }

  public function read($id) {
    _error_log("XXX read: \"$id\"\n");
    try {
      $ret = $this->scalaris_get($id . '.exists');
    } catch(ScalarisNotFoundException $e) {
//      _error_log("XXX is new");
      try {
        $this->scalaris_put($id . '.exists', 'exists');
        return '';
      } catch (ScalarisException $e) {
        return FALSE;
      }
    }
    if ($ret != 'exists') {
      $this->scalaris_put($id . '.exists', 'exists');
      return '';
    }
//    _error_log("XXX is old");
    try {
      return $this->scalaris_get($id);
    } catch (ScalarisException $e) {
      return FALSE;
    }
  }

  public function write($id, $data) {
    _error_log('XXX write: "' . $id . '", "' . $data. '"' . "\n");
    $ret = NULL;
    try {
      $ret = $this->scalaris_get($id . '.exists');
    } catch(ScalarisNotFoundException $e) {
      // do not put value
      _error_log('XXX write did not find .exists');
      return TRUE;
    } catch(ScalarisException $e) {
      _error_log('Scalaris Exception');
      return FALSE;
    }
    if ($ret == 'exists') {
      _error_log('XXX write .exists == exists');
      $this->id = $id;
      $this->data = $data;
      _error_log("XX writing data");
      try {
        if($this->scalaris_put($this->id, $this->data)) {
          return TRUE;
        }
        else return FALSE;
      } catch(ScalarisException $e) {
        return FALSE;
      }
    }
    else {
      _error_log('XXX write .exists == ' . print_r($ret, TRUE));
      return TRUE;// do not put value
    }
  }

  public function destroy($id) {
//    _error_log("XXX destroy: \"$id\"");
    try {$ret1 = $this->scalaris_put($id . '.exists', NULL);} catch(ScalarisException $e) {$ret1 = FALSE;}
    try {$ret2 = $this->scalaris_put($id, NULL);} catch(ScalarisException $e) {$ret2 = FALSE;}
    return $ret1 && $ret2;
  }

  public function gc($maxlifetime) {
//    _error_log("XXX gc: \"$maxlifetime\"");
    return true;
  }
}

$session_manager = new Scalaris();
session_set_save_handler(
  array($session_manager, 'open'),
  array($session_manager, 'close'),
  array($session_manager, 'read'),
  array($session_manager, 'write'),
  array($session_manager, 'destroy'),
  array($session_manager, 'gc')
);

?>
