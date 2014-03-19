#!/bin/bash

# set -x

C="DE"
ST="Berlin"
L="Berlin"
O="Contrail"
OU="" # Might be overwritten (for user certificates, OU is used for the superuser).
CN="" # Will be overwritten with the host/service idendifier or username:group
MAIL="info@conpaas.eu"

CA_DIR="/etc/cpsmanager/certs/"
CERT="cert.pem"
KEY="key.pem"
SERIAL="ca.srl" # will be created if not existing

DEFAULT_PASSPHRASE="passphrase"
DEFAULT_PASSPHRASE_JKS="jks_passphrase"

printUsage(){
  cat << EOF
Synopsis
  `basename $0` [-d] [-m] [-o] [-c] [-u USER] [-s] [-g GROUP] [-p PASSPHRASE ]
        [-t [-k PASSPHRASE_TRUSTSTORE]]
  Create signed certificates and export them to pkcs12. The CA to sign the
  created certificates is assumed to be ca/cert.pem and ca/key.pem.

  -d dir certificate
    Create a host certificate for the DIR server.

  -m mrc certificate
    Create a host certificate for the MRC server.

  -o osd certificate
    Create a host certificate for the OSD server.

  -c client certificate
    Create a service certificate for the client.

  -u user certificate
    Create a user certificate with the given name. The name will be used as user-
    name.

  -s superuser
    Creates the user as a superuser (i.e. puts xtreemfs-admin into the OU field).

  -g groupname
    The groupname for the user certificate.

  -p passphrase
    The passphrase for the pkcs12 files. If no passphrase is given, "passphrase"
    will be used as default.

  -t truststore
    Create a truststore from the CA certificate.

  -k truststore passphrase
    The pasphrase for the truststore. If no passphrase is given, "jks_passphrase"
    will be used as default.

  Example
  `basename $0` -u tester -p password
    Creates a certificate for the user "tester" with the passphrase "password"

  `basename $0` -dmoc -p password -t -k password_jks
    Creates all host certificates, a client certificate and a truststore from the CA.

EOF
}

check_env(){
  if [ ! -e "$CA_DIR/$CERT" ]; then
    echo "Error: $CA_DIR/$CERT missing"
    exit 1
  fi
  if [ ! -e "$CA_DIR/$KEY" ]; then
    echo "Error: $CA_DIR/$KEY missing"
    exit 1
  fi
  # create serial number if not existing
  if [ ! -e "$CA_DIR/ca.srl" ]; then
    echo $(get_even_random) > "$CA_DIR/ca.srl"
  fi
}

build_subject(){
  cn=$1
  ou=$2

  if [ -n "$cn" ]; then
    CN="$cn"
  fi

  if [ -n "$ou" ]; then
    OU="$ou"
  fi

  if [ -n "$C" ]; then
    subject="/C=$C"
  fi
  if [ -n "$ST" ]; then
    subject="$subject/ST=$ST"
  fi
  if [ -n "$L" ]; then
    subject="$subject/L=$L"
  fi
  if [ -n "$O" ]; then
    subject="$subject/O=$O"
  fi
  if [ -n "$OU" ]; then
    subject="$subject/OU=$OU"
  fi
  if [ -n "$CN" ]; then
    subject="$subject/CN=$CN"
  fi
  if [ -n "$MAIL" ]; then
    subject="$subject/emailAddress=$MAIL"
  fi
  echo ${subject}
}

create_certificate(){
    name=$1
    subject=$2
    generate_certificate $name $subject
    sign_certificate $name
    export_certificate $name
}

generate_certificate(){
  name=$1
  subject=$2

  openssl req -new \
    -subj $subject \
    -newkey rsa:1024 -nodes -out $name.req -keyout $name.key
  if [ $? -ne 0 ]; then exit 1; fi
}

sign_certificate(){
  name=$1
  openssl x509 -CA $CA_DIR/$CERT -CAkey $CA_DIR/$KEY -CAserial $CA_DIR/$SERIAL \
    -req -in $name.req -out $name.pem -days 365
  if [ $? -ne 0 ]; then exit 1; fi
}

export_certificate(){
  name=$1
  openssl pkcs12 -export -in $name.pem -inkey $name.key -out $name.p12 -name "$name" \
    -passout pass:$passphrase
  if [ $? -ne 0 ]; then exit 1; fi
}

create_truststore(){
  if [ -e "trusted.jks" ]; then
    echo "Error: Truststore (trusted.jks) already exists"
    exit 1
  fi

  keytool -import -alias ca -keystore trusted.jks -trustcacerts \
    -file "$CA_DIR/$CERT" <<EOF
${passphrase_jks}
${passphrase_jks}
yes
EOF
  if [ $? -ne 0 ]; then exit 1; fi
}

get_even_random(){
  random=$RANDOM
  length=$(expr length $random)
  until [ `expr $length % 2` -eq 0 ]; do
    random=$RANDOM
    length=$(expr length $random)
  done
  echo $random
}

################################################################################
## MAIN PROGRAM
################################################################################

# show usage if invoked without options/arguments
if [ $# -eq 0 ]; then
  printUsage
  exit 1
fi

check_env


## Parse options ##

# default values
passphrase=$DEFAULT_PASSPHRASE
passphrase_jks=$DEFAULT_PASSPHRASE_JKS
superuser=false
truststore=false

while getopts ":dmocu:sg:p:tk:h" opt; do
  case $opt in
    d) # dir
      certs="$certs dir"
      ;;
    m) # mrc
      certs="$certs mrc"
      ;;
    o) # osd
      certs="$certs osd"
      ;;
    c) # client
      certs="$certs client"
      ;;
    u) # user cerfiticate
      certs="$certs $OPTARG"
      ;;
    s) # user is superuser
      superuser=true
      ;;
    g) # group
      group="$OPTARG"
      ;;
    p) # passphrase for pkcs12
      passphrase=$OPTARG
      ;;
    t) # create truststore
      truststore=true
      ;;
    k) # truststore passphrase
      passphrase_jks=$OPTARG
      ;;
    h) # help
      printUsage
      exit 0
      ;;
    \?) # error handling
      echo "Error: Invalid option: -$OPTARG" >&2
      exit 1
      ;;
    :) # error handling
      echo "Error: Option -$OPTARG requires an argument." >&2
      exit 1
      ;;
  esac
done

for cert in $certs; do
  if [ "$cert" = "dir" ]; then
    subject=$( build_subject "host\/dir" )
    create_certificate dir $subject
  elif [ "$cert" == "mrc" ]; then
    subject=$( build_subject "host\/mrc" )
    create_certificate mrc $subject
  elif [ "$cert" == "osd" ]; then
    subject=$( build_subject "host\/osd" )
    create_certificate osd $subject
  elif [ "$cert" == "client" ]; then
    subject=$( build_subject "xtreemfs-service\/client" )
    create_certificate client $subject
  else # user certificates
    if [ -z "$group" ]; then
      group=$cert # if no group name was given, the group is set to the username
    fi
    # CN is set to user:group
    if $superuser ; then
      subject=$( build_subject "$cert:$group" "xtreemfs-admin")
    else
      subject=$( build_subject "$cert:$group" )
    fi
    create_certificate $cert $subject
  fi
done

if $truststore ; then
  create_truststore
fi

echo "SUCCESS: All certificates created"
