#!/bin/bash

txtdef="\e[0m" # revert to default color
errcolor="\e[1;31m" # bold red

errfile="out.err"
: > $errfile


# Takes as parameter "$@".
function parse_script_arguments {
    arch=
    datastore=
    description="no-description"
    vm_name=
    logging=false
    img_file=

    while :
    do
        case $1 in
            -a | --arch)
                arch=$2
                shift 2
                ;;
            -d | --description)
                description=$2
                shift 2
                ;;
            -h | --help)
                usage
                exit 0
                ;;
            -l | --logging)
                logging=true
                shift
                ;;
            -n | --name)
                vm_name=$2
                shift 2
                ;;
            -s | --datastore)
                datastore=$2
                shift 2
                ;;
            --) # End of all options.
                shift
                break
                ;;
            -*)
                warning "Unknown option (ignored): $1"
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    ## The image file ##
    if [ $# -ne 1 ] || [[ $1 != *.img ]]; then
        error_no_exit "Script must be called with just one parameter \
(excluding options), which is the image file: '<file-name>.img'.\nAll options must \
preced the image file name.\n"
        usage >&2
        exit 1
    fi

    img_file="$1"

    ## Some checks ##
    if ! silent_check arch; then
        xen_arch=$(parse_cfg_file xen_arch)
        kvm_arch=$(parse_cfg_file kvm_arch)
        hypervisor=$(parse_cfg_file hypervisor)

        if [ "$hypervisor" == kvm ]; then
            arch=$kvm_arch
        elif [ "$hypervisor" == xen ]; then
            arch=$kvm_arch
        else
            error "The hypervisor option is not properly set in '$cfg_file'.\n"
        fi
    fi
    [ $arch == "i386" ] || [ $arch == "amd64" ] || {
        error_no_exit "'arch' option is not properly set. It can be \
specified on the command line or read from the configuration file \
used to create the image, '$cfg_file', if this file exists in the \
current directory.\n"
        usage >&2
        exit 1
    }

    if ! silent_check datastore; then
        error_no_exit "'datastore' option is not set.\n"
        usage >&2
        exit 1
    fi

    if ! silent_check description; then
        error_no_exit "'description' option is not properly set.\n"
        usage >&2
        exit 1
    fi

    if ! silent_check vm_name; then
        vm_name=${img_file%.img}
    fi
}


function usage {
    out "Usage:\n$0
\t[-a | --arch <amd64 | i386>]
\t[-d | --description <description>]
\t[-h | --help]
\t[-l | --logging]
\t[-n | --name <vm-name>]
\t[-s | --datastore <opennebla-datastore-id>
\t<image-file>\n"
}


cfg_file=create-img-script.cfg
# Requires: $1 = name of configuratio option to search for.
# Output: The option if it is found in the configuratio file.
function parse_cfg_file {
    if ! [ -f $cfg_file ]; then
        echo -n ""
        return
    fi

    local re="^[[:space:]]*${1}[[:space:]]*="
    while read line; do
        if [[ "$line" =~ $re ]]; then
            echo -n ${line#*=}
            return
        fi
    done < $cfg_file
    echo -n ""
}


# Requires: $img_file, $vm_name
# Output: The file name of the image template.
function mk_img_template_file {
    check img_file vm_name
    local filename=$(mktemp)
    local path_to_img=$(readlink -f $img_file)

    cat <<EOF > $filename
NAME = "$vm_name"
PATH = $path_to_img
PUBLIC        = YES
DESCRIPTION   = "$description"
EOF

    echo $filename
}


# Requires: $arch, $vm_name
# Output: The file name of the vm template.
function mk_vm_template_file {
    check arch vm_name
    local filename=$(mktemp)
    local vm_arch=""
    [ $arch == amd64 ] && vm_arch=x86_64
    [ $arch == i386 ] && vm_arch=i686

    cat <<EOF > $filename
NAME = $vm_name
CPU    = 1
MEMORY = 1024

DISK   = [
  image_id = TODO,
  driver = raw,
  target   = "hda",
  readonly = "no" ]

NIC    = [network_id=1]
OS = [
  arch = $vm_arch
]

GRAPHICS = [
 TYPE    = "vnc",
 LISTEN  = "0.0.0.0"
]

FEATURES=[ acpi="yes" ]

CONTEXT = [
    hostname   = "\$NAME",
    dns        = "\$NETWORK[DNS,     NETWORK_ID=1]",
    gateway    = "\$NETWORK[GATEWAY, NETWORK_ID=1]",
    netmask    = "\$NETWORK[NETMASK, NETWORK_ID=1]",
    ip_private = "\$NIC[IP, NETWORK_ID=1]",
    userdata       = "
23212f62696e2f626173680a200a6966205b202d66202f6d6e742f636f6e
746578742e7368205d3b207468656e0a20202e202f6d6e742f636f6e7465
78742e73680a66690a0a686f73746e616d652024484f53544e414d450a69
66636f6e6669672065746830202449505f50524956415445206e65746d61
736b20244e45544d41534b200a726f757465206164642064656661756c74
2067772024474154455741592065746830200a0a6563686f20226e616d65
7365727665722024444e5322203e202f6574632f7265736f6c762e636f6e
660a200a2320546f206d616b652073736820776f726b20696e2044656269
616e204c656e6e793a0a236170742d67657420696e7374616c6c20756465
760a236563686f20226e6f6e65202f6465762f7074732064657670747320
64656661756c74732030203022203e3e202f6574632f66737461620a236d
6f756e74202d610a",
    target = "hdc"
]

  RAW = [ type = "kvm",
          data = "<devices><serial type=\\"pty\\"><source path=\\"/dev/pts/5\\"/><target port=\\"0\"/></serial><console type=\\"pty\\" tty=\\"/dev/pts/5\\"><source path=\\"/dev/pts/5\\"/><target port=\\"0\\"/></console></devices>" ]
EOF

    echo $filename
}


# Requires: $1 = the filename with the image template.
#           $2 = the filename with the vm template.
#           $datastore
function create_vm {
    check datastore
    local out=$(oneimage create $1 -d $datastore)
    local rc=$?
    echo $out
    [ $rc != 0 ] && exit $rc
    [[ $out =~ Error ]] && exit 1

    local img_id=$(echo $out | awk '{print $2}')
    sed -i "s/^  image_id =.*/  image_id = $img_id,/g" $2

    while :
    do
        sleep 5
        out=$(onevm create $2)
        rc=$?
        echo $out

        [ $rc == 0 ] && break

        echo "Trying again ..."
    done

    local vm_id=$(echo $out | awk '{print $2}')
    out=$(onevm show $vm_id | grep IP)
    local vm_ip=$(echo $out | grep "IP=" | awk -F\" '{print $2}')

    while :
    do
        sleep 5
        out=$(onevm list | grep $vm_id)
        echo "$out"
        echo "$out" | grep "runn" > /dev/null
        rc_grep=${PIPESTATUS[1]}
        [ $rc_grep == 0 ] && break
    done

    echo img id: $img_id
    echo vm id: $vm_id
    echo vm ip: $vm_ip
}


function silent_check {
    for x in "$@" ; do
        [ -z "${!x}" ] && return 1
    done
    return 0
}


function check {
    for x in "$@" ; do
        [ -z "${!x}" ] &&  error "$x is not set."
    done
    :
}


# Each arg of 'error_no_exit' is a line.
function error_no_exit {
    for line in "$@"; do
        if [ $logging == true ]; then
            out "${errcolor}ERROR: $line$txtdef\n" "ERROR: $line\n" $errfile >&2
        else
            out "${errcolor}ERROR: $line$txtdef\n" >&2
        fi
    done
}


# Each arg of 'error' is a line.
function error {
    error_no_exit "$@"
    exit 1
}


# Each arg of 'warning' is a line.
function warning {
    for line in "$@"; do
        if [ $logging == true ]; then
            out "${errcolor}WARNING: $line$txtdef\n" "WARNING: $line\n" $errfile >&2
        else
            out "${errcolor}WARNING: $line$txtdef\n" >&2
        fi
    done
}


# Output function, takes $msg, $filemsg and $file args in that order.
function out {
    printf -- "$1"

    if [ -n "$3" ]; then
        printf -- "$2" >>$3
    fi
}



parse_script_arguments "$@"
img_template=$(mk_img_template_file)
vm_template=$(mk_vm_template_file)
create_vm $img_template $vm_template
rm $img_template $vm_template

