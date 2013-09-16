#/bin/bash
# Register EBS backed AMI.

# Stop execution if any command fails.
#set -e

txtdef="\e[0m" # revert to default color
txtbld="\e[1m"    # bold
txtgreen="\e[0;32m"
errcolor="\e[1;31m" # bold red
logcolor="\e[0;34m" # blue

logfile="out.log"
errfile="out.err"
: > $logfile
: > $errfile


# Requires: $img_file
# Output: $logfile, $errfile, $work_dir, $volume_size, $EC2_ACCESS_KEY, $EC2_SECRET_KEY
function init_variables {
    work_dir="work-dir"

    rm -rf $work_dir
    mkdir $work_dir

    local size=`du -B M $img_file | awk -F M '{print $1}'`
    volume_size=$((size / 1024))
    if [ $((size % 1024)) -ne 0 ]; then
        (( volume_size += 1 ))
    fi

    : ${EC2_ACCESS_KEY:?"You need to set env variable: 'EC2_ACCESS_KEY'."}
    : ${EC2_SECRET_KEY:?"You need to set env variable: 'EC2_SECRET_KEY'."}
}


function install_pkgs {
    # euca2ools dependencies.
    host_pkgs=('python-boto')
    host_pkgs+=('python-m2crypto')
    host_pkgs+=('build-essential')

    # Other tools.
    host_pkgs+=('mount')        # losetup, mount, umount
    host_pkgs+=('kpartx')       # kpartx
    host_pkgs+=('parted')       # parted
    host_pkgs+=('e2fsprogs')    # tune2fs
    host_pkgs+=('grub2')        # grub-install

    # Other tools
    host_pkgs+=('grub-pc')

    apt-get update
    apt-get install -y ${host_pkgs[*]} | spin
    [ $PIPESTATUS == 0 ] || die "Installing host packages failed!"

    modprobe dm-mod
}


function usage {
    echo -e "Usage:\n$0
\t[-a | --arch <amd64 | i386>]
\t[-d | --description <description>]
\t[-h | --help]
\t[-n | --name <ami-name>]
\t<image-file>"
}


# Takes as parameter "$@".
function parse_script_arguments {
    arch=
    availability_zone=
    description="no-description"
    ami_name=

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
            -n | --name)
                ami_name=$2
                shift 2
                ;;
            --) # End of all options.
                shift
                break
                ;;
            -*)
                echo "${errcolor}WARN: Unknown option (ignored): $1${txtdef}" >&2
                shift
                ;;
            *)
                break
                ;;
        esac
    done

    # The image file.
    if [ $# -ne 1 ] || [[ $1 != *.img ]]; then
        echo -e "${errcolor}ERROR: Script must be called with just one parameter \
(excluding options), which is the image file: 'file-name.img'.\nAll options must \
preced the image file name.\n${txtdef}" >&2
        usage >&2
        exit 1
    fi

    img_file="$1"

    # Some checks.
    if ! silent_check arch; then
        arch=$(parse_cfg_file xen_arch)
    fi
    [ $arch == "i386" ] || [ $arch == "amd64" ] || {
        echo -e "${errcolor}ERROR: 'arch' option is not properly set. It can be \
specified on the command line or in a file called '${cfg_file}'.\n${txtdef}" >&2
        usage >&2
        exit 1
    }

    if ! silent_check description; then
        echo -e "${errcolor}ERROR: 'description' option is not properly set.\n${txtdef}" >&2
        usage >&2
        exit 1
    fi

    if ! silent_check ami_name; then
        ami_name=${img_file%.img}
    fi
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


# Requires: $work_dir
# Output: --
function check_euca2ools {
    check work_dir

    # Install the euca2ools if they are not installed or the version is wrong
    if ! command -v euca-version > /dev/null 2>&1; then
        install_euca2ools
    elif [[ ! "`euca-version`" =~ euca2ools\ 2.0.* ]]; then
        install_euca2ools
    fi
}


# Requires: $work_dir
# Output: --
function install_euca2ools {
    # We want to fail if make fails, so don't start a subshell with ()
    # Remember the old dir
    local orig_pwd=$(pwd)

    out "${txtgreen}Installing euca2ools...\n${txtdef}"
    # Install euca2ools.
    # Download sources for versions 2.0.2
    wget -qO euca2ools-1.3.2.tar.gz https://github.com/eucalyptus/euca2ools/archive/1.3.2.tar.gz
    tar zxf euca2ools-1.3.2.tar.gz

    cd euca2ools-1.3.2
    make | spin
    [ $PIPESTATUS == 0 ] || die "Installation of euca2ools failed!"
    cd $orig_pwd

    apply_boto_patch
}


function apply_boto_patch {
    local boto_ec2_dir='/usr/share/pyshared/boto/ec2'
    local patch_url='https://bugzilla.redhat.com/attachment.cgi?id=455857'
    if [ -r "$boto_ec2_dir/blockdevicemapping.py" ]; then
        local result=$(
            grep -q "pre = '%sBlockDeviceMapping.%d' % (pre, i)" $boto_ec2_dir/blockdevicemapping.py
            echo $?)
        if [ $result -eq 0 ]; then
            wget -qO - $patch_url | patch -sfr - -d $boto_ec2_dir
            [ $PIPESTATUS == 0 ] || die "Unable to patch boto."
        fi
    fi
}


# Requires: --
# Output: $instance_information, $instance_id, $region, $availability_zone, $EC2_URL
function get_host_info {
    instance_information=`wget -qO - http://169.254.169.254/latest/dynamic/instance-identity/document`

    # We need the region, for the apt sources and the availability zone for the EBS volume
    instance_id=`printf -- "$instance_information" | grep instanceId | awk -F\" '{print $4}'`
    region=`printf -- "$instance_information" | grep region | awk -F\" '{print $4}'`
    availability_zone=`printf -- "$instance_information" | grep availabilityZone | awk -F\" '{print $4}'`

    if [ -z "$instance_id" ]; then
        die \
            "Unable to fetch the instance id of this machine." \
            "This script must be running on ec2 in order to mount EBS volumes."
    fi

    [ -z "$region" ] && die "Unable to fetch the region of this machine."
    [ -z "$availability_zone" ] && die "Unable to fetch the availability zone of this machine."

    export EC2_URL="https://ec2.$region.amazonaws.com"

    log "instance_information: $instance_information"
    log "EC2_URL=$EC2_URL"

#    # Check if we can handle this region, there are hardcoded AKIs later on.
#    if ! $(contains $region known_regions[@]); then
#        die "The region $region is unkown."
#    fi
}


# Requires: $volume_size, $availability_zone
# Output: $volume_id
function create_ebs_volume {
    check volume_size availability_zone

    volume_id=`euca-create-volume --size $volume_size --zone "$availability_zone" | awk '{print $2}'`

    [ -z "$volume_id" ] && die "Unable to create volume."
    dotdot "euca-describe-volumes $volume_id | grep available > /dev/null && echo available"
    log "The EBS volume id is $volume_id"
}


# Requires: $instance_id, $volume_id
# Output: $device_path
function attach_ebs_volume {
    check instance_id volume_id

    # Get a random device letter, we will hang forever if we try to attach a volume to an already mapped device.
    for device_letter in {f..z}; do
        device_path="/dev/xvd$device_letter"
        [ ! -b $device_path ] && break
    done
    [ -b $device_path ] && die "No free device letters found (tried sdf to sdz)!"

    euca-attach-volume --instance "$instance_id" --device "/dev/sd$device_letter" "$volume_id"
    # Wait until the volume is attached
    dotdot "test -b $device_path && echo attached"
    log "The EBS device is $device_path"
}


# Requires: $img_file, $device_path
# Output: --
function cp3_img_to_ebs_volume {
    check img_file device_path

    mkfs.ext3 $device_path
    tune2fs -i 0 $device_path

    # Mounting dst.
    local dst_dir=$(mktemp -d)
    mount $device_path $dst_dir
    log "The volume is mounted at $dst_dir"

    # Mounting source image.
    local src_loop=$(losetup -f)
    losetup $src_loop $img_file

    partition=$(kpartx -l $src_loop | awk '{ print $1 }')
    partition=/dev/mapper/$partition
    kpartx -a $src_loop

    local src_dir=$(mktemp -d)
    mount -o loop $partition $src_dir

    # Copy files.
    ( cd $src_dir && tar -cf - . ) | ( cd $dst_dir && tar -xpf - )

    # Mount all the different special devices, other installers depend on their existence
    mount --bind /dev $dst_dir/dev
    chroot $dst_dir mount -t proc none /proc
    chroot $dst_dir mount -t sysfs none /sys
    chroot $dst_dir mount -t devpts none /dev/pts

    # Grub
    chmod -x $dst_dir/etc/grub.d/*
    cp 40_custom  $dst_dir/etc/grub.d/40_custom
    chmod 755 $dst_dir/etc/grub.d/40_custom

    sed -i "s/^GRUB_TIMEOUT=[0-9]\+/GRUB_TIMEOUT=0\nGRUB_HIDDEN_TIMEOUT=true/" $dst_dir/etc/default/grub

    # Update grub.cfg using the script
    chroot $dst_dir update-grub

    # Alias grub.cfg as menu.lst
    chroot $dst_dir rm -rf /boot/grub/menu.lst
    chroot $dst_dir ln -s /boot/grub/grub.cfg /boot/grub/menu.lst

    # We unmount from inside the image, otherwise the system won't boot
    chroot $dst_dir umount /dev/pts
    chroot $dst_dir umount /sys
    chroot $dst_dir umount /proc
    umount $dst_dir/dev

    umount $dst_dir
    rmdir $dst_dir

    umount $src_dir
    kpartx -d $src_loop
    losetup -d $src_loop
    rmdir $src_dir

}

function write_fstab {
    check device_path

    # Mounting dst.
    local dst_dir=$(mktemp -d)
    mount $device_path $dst_dir

    local mountoptions=',barrier=0'
    cat > $dst_dir/etc/fstab <<EOF
/dev/xvda1 /     ext3    defaults$mountoptions 1 1
EOF

    umount $dst_dir
    rmdir $dst_dir

}


# Requires: $volume_id
# Output: --
function detach_ebs_volume {
    check volume_id

    euca-detach-volume $volume_id
    dotdot "euca-describe-volumes $volume_id | grep 'available' > /dev/null && echo Detached."
}


# Requires: $volume_id
# Output: $snapshot_id
function create_ebs_snapshot {
    check volume_id

    logn "Creating snapshot of the EBS volume"
    snapshot=`euca-create-snapshot $volume_id`
    [ -z "$snapshot" ] && die "\nUnable to create snapshot from the volume '$volume_id'"
    snapshot_id=`printf -- "$snapshot" | awk '{print $2}'`

    # Wait for the snapshot to be completed, can take quite some time
    dotdot "euca-describe-snapshots $snapshot_id | grep 'completed'"
}


# Requires: $volume_id
# Output: --
function delete_ebs_volume {
    check volume_id

    log "Deleting the volume"
    euca-delete-volume $volume_id
}



# Requires: $region, $arch
# Output: $aki
function set_aki {
    check region arch

    log "Set aki"
    # Figure out which pvGrub kernel ID we need.
    case $region in
        us-east-1)
            [ $arch = 'amd64' ] && aki="aki-88aa75e1"
            [ $arch = 'i386' ] && aki="aki-b6aa75df"
        ;;
        us-west-1)
            [ $arch = 'amd64' ] && aki="aki-f77e26b2"
            [ $arch = 'i386' ] && aki="aki-f57e26b0"
        ;;
        us-west-2)
            [ $arch = 'amd64' ] && aki="aki-fc37bacc"
            [ $arch = 'i386' ] && aki="aki-fa37baca"
        ;;
        eu-west-1)
            [ $arch = 'amd64' ] && aki="aki-71665e05"
            [ $arch = 'i386' ] && aki="aki-75665e01"
        ;;
        ap-southeast-1)
            [ $arch = 'amd64' ] && aki="aki-fe1354ac"
            [ $arch = 'i386' ] && aki="aki-f81354aa"
        ;;
        ap-southeast-2)
            [ $arch = 'amd64' ] && aki="aki-31990e0b"
            [ $arch = 'i386' ] && aki="aki-33990e09"
        ;;
        ap-northeast-1)
            [ $arch = 'amd64' ] && aki="aki-44992845"
            [ $arch = 'i386' ] && aki="aki-42992843"
        ;;
        sa-east-1)
            [ $arch = 'amd64' ] && aki="aki-c48f51d9"
            [ $arch = 'i386' ] && aki="aki-ca8f51d7"
        ;;
        us-gov-west-1)
            [ $arch = 'amd64' ] && aki="aki-79a4c05a"
            [ $arch = 'i386' ] && aki="aki-7ba4c058"
        ;;
        *) die "Unrecognized region:" "$region"
    esac

}


# Requires: $arch, $ami_name, $description, $aki, $snapshot_id, $volume_size
# Output: $ami_id
function register_ebs_ami {
    check arch ami_name description aki snapshot_id volume_size

    [ $arch = 'i386' ] && ami_arch='i386'
    [ $arch = 'amd64' ] && ami_arch='x86_64'

    # The AMI has to start with "debian", otherwise we won't get a nice icon
    # The ":N:true:standard" is necessary so that the root volume
    # will be deleted on termination of the instance (specifically the "true" part)
    log "Registering an AMI with the snapshot '$snapshot_id'"
    ami_id=`euca-register \
        --name "$ami_name" --description "$description" \
        --architecture "$ami_arch" --kernel "$aki" \
        #--root-device-name  /dev/sda1 \
        --snapshot "$snapshot_id:$volume_size:true:standard" \
        | awk '{print $2}'`

    # If the user has already created an unnamed AMI today,
    # this will fail, so give the AMI registration command to the user
    if [[ ! "$ami_id" =~ ^ami-[0-9a-z]{8}$ ]]; then
        die \
            "Unable to register an AMI." \
            "You can do it manually with:" \
            "export EC2_URL=\"$EC2_URL\"" \
            "`which euca-register` \\\\" \
            "--name '$ami_name' --description '$description' \\\\" \
            "--architecture '$ami_arch' --kernel '$aki' \\\\" \
            "--snapshot '$snapshot_id:$volume_size:true:standard'"
    fi
    log "Your AMI has been created with the ID '$ami_id'"
}


function clean {
    rm -rf $work_dir
}


# # # # # # # # # # # # # # # # # # # # # # # #


# Each arg of log is a line.
function log {
    for line in "$@"; do
        out "$logcolor$line$txtdef\n" "$line\n" $logfile
    done
}


# Log without the newline.
function logn {
    out "$logcolor$1$txtdef" "$1" $logfile
}


# Each arg of die is a line.
function die {
    for line in "$@"; do
        out "$errcolor$line$txtdef\n" "$line\n" $errfile >&2
    done
    exit 1
}


function spin {
    local cursor='|'
    local cols=$(( `tput cols` - 2 ))
    while read line; do
        printf -- "\r$logcolor$cursor$txtdef %-${cols}s" "${line:0:$cols}"
        case $cursor in
            '|') cursor='/' ;;
            '/') cursor='-' ;;
            '-') cursor='\\' ;;
            '\\') cursor='|' ;;
        esac
    done
    printf "\n"
}


# Wait for the execution of $cmd not to return an empty string.
function dotdot {
    local cmd=$1
    local status=`eval $cmd`
    local sleep=5
    [ ! -z "$2" ] && sleep=$2
    while [ -z "$status" ]; do
        logn '.'
        sleep $sleep
        # Don't error out if the command fails.
        status=`eval $cmd || true`
    done
    logn "\n"
}


# Output function, takes $msg, $filemsg and $file args in that order.
function out {
    printf -- "$1"

    if [ -n "$3" ]; then
        printf -- "$2" >>$3
    fi
}


function silent_check {
    for x in "$@" ; do
        [ -z "${!x}" ] && return 1
    done
    return 0
}


function check {
    for x in "$@" ; do
        [ -z "${!x}" ] && { echo -e "${errcolor}ERROR: $x is not set.${txtdef}" >&2 ; exit 1 ; }
    done
    :
}

# # # # # # # # # # # # # # # # # # # # # # # #

parse_script_arguments "$@"
init_variables "$@"
get_host_info
install_pkgs
check_euca2ools
create_ebs_volume
attach_ebs_volume
cp3_img_to_ebs_volume
write_fstab
detach_ebs_volume
create_ebs_snapshot
delete_ebs_volume
set_aki
register_ebs_ami
clean


