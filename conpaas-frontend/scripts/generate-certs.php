<?php

// This script generates the self-signed certificate of the CA
// and the certificate of the frontend, signed by the CA.

// Usage:
//    $ php generate-certs.php dir_name
//
//    where dir_name is path to the directory where to put the
//    generated certificates 

// To visualize the generated files you can use:
//    $ openssl rsa -in ca_key.pem -text -noout
//    $ openssl x509 -in ca_cert.pem -text -noout
//
//    $ openssl rsa -in key.pem -text -noout
//    $ openssl x509 -in cert.pem -text -noout

if(!isset($argv[1])) {
    echo 'Please supply the path where to put the certificates.'.PHP_EOL;
    exit(1);
}

$dir = $argv[1];

class CA {
    private $cakey = null;
    private $cacert = null;
    private $period = 365; //cert valid for 1 year 

    public function __construct() {
        //Generate key and CA's certificate
        $dn = array(
            "organizationName" => "ConPaaS",
            "emailAddress" => "info@conpaas.eu",
            "commonName" => "CA"
        );

        $this->cacert = $this->get_cert('ca_key.pem', 'ca_cert.pem',
                                        $dn, null, rand());
    }

    public function get_cert($key_file, $cert_file,
                             $dn, $configs, $serial) {
        global $dir;
                         
        //Generate the key
        $key = $this->get_key($key_file);

        //Update the CA's key
        if ($this->cakey == null)
            $this->cakey = $key;

        //Generate a certificate signing request
        $csr = openssl_csr_new($dn, $key);

        //Sign the request
        $cert = openssl_csr_sign($csr, $this->cacert, 
            $this->cakey, $this->period, $configs, $serial);

        //Write certificate to file
        openssl_x509_export($cert, $csrout, FALSE);
        file_put_contents($dir.'/'.$cert_file, $csrout);
        return $cert;
    }

    public function get_key($filename) {
        global $dir;
        $key = openssl_pkey_new();
        openssl_pkey_export($key, $key_out);
        file_put_contents($dir.'/'.$filename, $key_out);
        return $key;
    }
}

// Try to guess server hostname
$hostname = null;
$conffile = "/var/www/config.php";

if (is_readable($conffile)) {
    require_once($conffile);
    $hostname = CONPAAS_HOST;
}
else {
    $hostname = gethostname();
}

// Prompt for confirmation
echo "Is your frontend public hostname '".$hostname."'? (Y/n) ";
$confirm = rtrim(fgets(STDIN), "\n");

if ($confirm === "n" || $confirm === "N") {
    echo "Please specify the public hostname of your frontend: ";
    $hostname = rtrim(fgets(STDIN), "\n");
}

$ca = new CA();

//FE's certificate
$configs = array('x509_extensions' => 'v3_req');
$dn = array(
    "organizationName" => "ConPaaS",
    "emailAddress" => "info@conpaas.eu",
    "commonName" => $hostname,
    "role" => "frontend"
);
$ca->get_cert('key.pem', 'cert.pem',
              $dn, $configs, rand());

?>
