#!/bin/bash -e
# Build an EC2 bundle and upload/register it to Amazon

BUCKET=conpaas-imgs

# The credentials can also be given (or overwritten) when executing the script.
EC2_USER=           #TODO
EC2_ACCESS=         #TODO
EC2_ACCESS_SECRET=  #TODO

[ -z "$JAVA_HOME" ] && JAVA_HOME=                   #TODO
[ -z "$EC2_HOME" ] && EC2_HOME=                     #TODO
[ -z "$EC2_AMITOOL_HOME" ] && EC2_AMITOOL_HOME=     #TODO
[ -z "$AWS_IAM_HOME" ] && AWS_IAM_HOME=$EC2_HOME
[ -z "$EC2_PRIVATE_KEY" ] && EC2_PRIVATE_KEY=       #TODO
[ -z "$EC2_CERT" ] && EC2_CERT=                     #TODO
export JAVA_HOME EC2_HOME EC2_AMITOOL_HOME AWS_IAM_HOME EC2_PRIVATE_KEY EC2_CERT

PATH=$PATH:$EC2_AMITOOL_HOME:$EC2_HOME

USAGE="Usage: `basename $0` [-h] [-b <bucket-name>] [-u EC2-user-number] [-i EC2-Access-Key-Id] [-s EC2-Secret-Access-Key]  -f <image-file>  -n <ami-name>"

function check {
    for x in "$@" ; do
        [ -z "${!x}" ] && { echo ERROR: $x is not set. >&2 ; exit 1 ; }
    done
    :
}


IMG=
AMI_NAME=
# Parse command line options.
while getopts hb:u:i:s:f:n: OPT; do
    case "$OPT" in
        h)
            echo $USAGE
            exit 0
            ;;
        b)
            BUCKET=$OPTARG
            ;;
        u)
            EC2_USER=$OPTARG
            ;;
        i)
            EC2_ACCESS=$OPTARG
            ;;
        s)
            EC2_ACCESS_SECRET=$OPTARG
            ;;
        f)
            IMG=$OPTARG
            ;;
        n)
            AMI_NAME=$OPTARG
            ;;
        \?)
            echo $USAGE >&2
            exit 1
            ;;
    esac
done

shift `expr $OPTIND - 1`
[ $# -ne 0 ] && { echo $USAGE >&2 ; exit 1 ; }

check BUCKET EC2_USER EC2_ACCESS EC2_ACCESS_SECRET JAVA_HOME EC2_HOME AWS_IAM_HOME EC2_PRIVATE_KEY EC2_CERT

[ -z "$AMI_NAME" ] && { echo $USAGE >&2 ; exit 1 ; }
[ -z "$IMG" ] && { echo $USAGE >&2 ; exit 1 ; }
[ -z "$EC2_AMITOOL_HOME" ] && echo WARNING: EC2_AMITOOL_HOME is not set. It will default to EC2_HOME.


EC2_TMP=`mktemp -d`
ec2-bundle-image -i ${IMG} -k ${EC2_PRIVATE_KEY} -c ${EC2_CERT} -u ${EC2_USER} -d $EC2_TMP --arch x86_64 --kernel aki-427d952b -B ami=sda,root=/dev/sda1,ephemeral0=sdb,swap=sdc
ec2-upload-bundle -b ${BUCKET} -m $EC2_TMP/$filename.manifest.xml -a ${EC2_ACCESS} -s ${EC2_ACCESS_SECRET}
ec2-register ${BUCKET}/$filename.manifest.xml -n $AMI_NAME --root-device-name /dev/sda --kernel aki-4e7d9527 -a x86_64 -K ${EC2_PRIVATE_KEY} -C ${EC2_CERT} 

du -sh $EC2_TMP
rm -rf $EC2_TMP
