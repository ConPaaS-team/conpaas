#!/usr/bin/python
# Copyright (c) 2010-2012, Contrail consortium.
# All rights reserved.
#
# Redistribution and use in source and binary forms,
# with or without modification, are permitted provided
# that the following conditions are met:
#
#  1. Redistributions of source code must retain the
#     above copyright notice, this list of conditions
#     and the following disclaimer.
#  2. Redistributions in binary form must reproduce
#     the above copyright notice, this list of
#     conditions and the following disclaimer in the
#     documentation and/or other materials provided
#     with the distribution.
#  3. Neither the name of the Contrail consortium nor the
#     names of its contributors may be used to endorse
#     or promote products derived from this software
#     without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
# OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Based on the asscociated configuration file, this script
# generates another script which creates VM images for
# ConPaaS, to be used for OpenNebula with KVM.

import sys, os, ConfigParser, stat

output_filename = None

def get_cfg_file_handle():
    configname = os.path.basename(__file__)
    configname, _ = os.path.splitext(configname)
    configname += '.cfg'

    config = ConfigParser.RawConfigParser()
    config.read(configname)

    return config

output_file = None

def create_output_file():
    global output_file
    output_file = open(output_filename, 'w')

def append_file_to_output(filename):
    src = open(filename, 'r')
    dst = output_file

    data = src.read()
    dst.write(data)

    src.close()

def append_str_to_output(string):
    dst = output_file
    dst.write(string)

def close_output_file():
    output_file.close()
    os.chmod(output_filename,
            stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
            stat.S_IRGRP | stat.S_IXGRP |
            stat.S_IXOTH)

if __name__ == '__main__':
    root_dir = 'scripts/'

    config = get_cfg_file_handle()

    output_filename = 'create-img-' + config.get('CUSTOMIZABLE', 'filename')[:-4] + '.sh'
    create_output_file()

    # Write head script
    filename = config.get('SCRIPT_FILE_NAMES', 'head_script')
    append_file_to_output(root_dir + filename)

    # Write script variables (defined in the configuration file)
    append_str_to_output('# Section: variables from configuration file\n\n')

    append_str_to_output('# The name and size of the image file '\
            'that will be generated.\n')
    append_str_to_output('FILENAME=' + config.get('CUSTOMIZABLE', 'filename') + '\n')
    append_str_to_output('FILESIZE=' + config.get('CUSTOMIZABLE', 'filesize') + '\n\n')

    append_str_to_output('# The Debian distribution that you would '\
            'like to have installed (we recommend squeeze).\n')
    append_str_to_output('DEBIAN_DIST=' + config.get('RECOMMENDED', 'debian_dist') + '\n')
    append_str_to_output('DEBIAN_MIRROR=' + config.get('RECOMMENDED', 'kvm_debian_mirror') + '\n\n')

    append_str_to_output('# The architecture and kernel version for '\
            'the OS that will be installed (please make\n')
    append_str_to_output('# sure to modify the kernel version name accordingly if you modify the architecture).\n')

    cloud = config.get('CUSTOMIZABLE', 'cloud')
    hypervisor = config.get('CUSTOMIZABLE', 'hypervisor')
    optimize = config.get('CUSTOMIZABLE', 'optimize')

    if cloud == 'opennebula':
        pass
    elif cloud == 'ec2':
        if hypervisor != 'xen':
            print 'WARNING: Your choice of hypervisor is not compatible with Amazon EC2. Xen will be used instead.'
            hypervisor = 'xen'
    else:
        print 'Choose a cloud.'
        sys.exit(1)

    append_str_to_output('CLOUD=' + cloud + '\n')

    if hypervisor == 'kvm':
        append_str_to_output('ARCH=' + config.get('RECOMMENDED', 'kvm_arch') + '\n')
        append_str_to_output('KERNEL_VERSION=' + config.get('RECOMMENDED', 'kvm_kernel_version') + '\n\n')
    elif hypervisor == 'xen':
        append_str_to_output('ARCH=' + config.get('RECOMMENDED', 'xen_arch') + '\n')
        append_str_to_output('KERNEL_VERSION="' + config.get('RECOMMENDED', 'xen_kernel_version') + '"\n\n')
    else:
        print 'Choose a hypervisor.'
        sys.exit(1)

    # Write message about the selected services
    print 'Setting up image for %s, with services:' % hypervisor.upper(),

    # Write general scripts
    filenames = config.get('SCRIPT_FILE_NAMES', 'general_scripts')
    for filename in filenames.split():
        append_file_to_output(root_dir + filename)

    # Write service scripts
    rm_script_args = ''
    for servicename, should_include in config.items('SERVICES'):
        if 'true' == should_include:
            rm_script_args += ' --' + servicename[:-8]
            filename = config.get('SCRIPT_FILE_NAMES', servicename + '_script')
            append_file_to_output(root_dir + filename)
            print servicename.replace('_service', '').upper(),
    print

    # Write rm script
    if optimize == 'true':
        filename = config.get('SCRIPT_FILE_NAMES', 'rm_script')
        append_file_to_output(root_dir + filename)
        append_str_to_output("RM_SCRIPT_ARGS=" + "'" + rm_script_args + "'\n\n")

    # Write user script
    filename = config.get('SCRIPT_FILE_NAMES', 'user_script')
    append_file_to_output(root_dir + filename)

    # Write tail script
    filename = config.get('SCRIPT_FILE_NAMES', 'tail_script')
    append_file_to_output(root_dir + filename)

    # Write contextualization script
    if cloud == 'opennebula':
        filename = config.get('SCRIPT_FILE_NAMES', 'opennebula_script')
    elif cloud == 'ec2':
        filename = config.get('SCRIPT_FILE_NAMES', 'ec2_script')
    append_file_to_output(root_dir + filename)

    # Write resize script
    if optimize == 'true':
        filename = config.get('SCRIPT_FILE_NAMES', 'resize_script')
        append_file_to_output(root_dir + filename)

    close_output_file()

    print "\nPlease run create-img-conpaas.sh as root"
