<?php

function _error_log($where, $msg) {
  error_log("$where: $msg\n", 3, '/tmp/scalaris-session.log');
}

class Scalaris {

  public function __construct() {
    $this->VAR_CACHE = '/var/cache/cpsagent/';
  }

  /**
   * Perform an http POST request to $this->path (supplied to open())
   * with parameters given in $params.
   *
   * @param array $params Associative array for parameters to JSON encode and send.
   *
   * Return the decoded json response on success, null on failure
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
    if ($response === false) {
      _error_log(__METHOD__ . ':' . __LINE__, 'HTTP request error calling ' . $this->path);
      return null;
    }

    $json_response = json_decode($response);
    if ($json_response === null) {
      _error_log(__METHOD__ . ':' . __LINE__, 'JSON decode error decoding ' . $response);
      return null;
    }

    return $json_response;
  }

  /**
   * Get the value to key from Scalaris.
   * Return value of key on success, null on failure
   *
   * @param string $key
   */
  private function scalaris_get($key) {
    $params = array();
    $params['version'] = '1.1';
    $params['id'] = 0;
    $params['method'] = 'read';
    $params['params'] = array($key);

    $response = $this->http_post($params);
    if ($response === null) {
        return null;
    }

    if (!isset($response->result) || !isset($response->result->status)) {
        return null;
    }

    if ($response->result->status === 'ok' && isset($response->result->value)) {
        return $response->result->value->value;
    }

    if ($response->result->status === 'fail' && isset($response->result->reason))
    {
        // logging failure reason if provided
        if ($response->result->reason !== "not_found") { 
            _error_log(__METHOD__ . ':' . __LINE__, 'GET failed: ' . $response->result->reason);
        }
    }

    return null;
  }

  /**
   * Write value to key.
   * Returns true on success, false on failure.
   *
   * @param string $key
   * @param string $value
   */
  public function scalaris_put($key, $value) {
    $params = array();
    $params['version'] = '1.1';
    $params['id'] = 0;
    $params['method'] = 'write';
    $params['params'] = array($key, array('type'=>'as_is', 'value'=>$value));

    $response = $this->http_post($params);
    if ($response === null) {
        return false;
    }

    if (!isset($response->result) || !isset($response->result->status)) {
        return false;
    }

    return $response->result->status === 'ok';
  }

  /**
   * Delete the given key from Scalaris.
   * Returns true on success, false on failure.
   */
  private function scalaris_delete($key) {
    $params = array();
    $params['version'] = '1.1';
    $params['id'] = 0;
    $params['method'] = 'delete';
    $params['params'] = array($key);

    $response = $this->http_post($params);
    if ($response === null) {
        return false;
    }

    if (!isset($response->result) || !isset($response->result->status)) {
        return false;
    }

    return $response->result->status === 'ok';
  }

  public function open($save_path, $session_name) {
    $this->path = file_get_contents($this->VAR_CACHE.'fpm-scalaris.conf');
    return true;
  }

  public function close() {
    return true;
  }

  public function read($id) {
    $res = $this->scalaris_get($id);
    return ($res === null) ? "" : $res;
  }

  public function write($id, $data) {
    return $this->scalaris_put($id, $data);
  }

  public function destroy($id) {
    return $this->scalaris_delete($id);
  }

  public function gc($maxlifetime) {
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

register_shutdown_function('session_write_close');
?>
