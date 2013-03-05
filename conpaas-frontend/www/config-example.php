<?php
// The URL of your ConPaaS director installation. Do not forget to include the
// port number (5555 by default)
const DIRECTOR_URL = 'https://director.yourdomain.com:5555';

// The CONPAAS_CONF_DIR variable to point to the directory containing your
// frontend's configuration files.
const CONPAAS_CONF_DIR = '/etc/cpsdirector';

// The HOST variable to contain the DNS name under  which your front-end will
// be accessible
const CONPAAS_HOST = 'conpaas.yourdomain.com';

// These parameters are used for performing CAPTCHA[1] operations and they are
// issued for a specific domain. To generate a pair of keys for your domain,
// please go to the reCAPTCHA admin page[2] (it's hosted by Google, so you need
// a Google account).
//
// [1] http://www.google.com/recaptcha
// [2] https://www.google.com/recaptcha/admin/create
const CAPTCHA_PRIVATE_KEY = 'YOUR_DOMAIN_CAPTCHA_PRIVATE_KEY';
const CAPTCHA_PUBLIC_KEY = 'YOUR_DOMAIN_CAPTCHA_PUBLIC_KEY';

// These parameters are used to indicate which cloud types are supported.
// If removed you wil get loads of error messages in /var/log/apache2/error.log
const enable_opennebula = "yes";
const enable_ec2 = "yes";
?>
