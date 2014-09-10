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

def error(error_msg):
    print 'ERROR: %s' % error_msg
    sys.exit(1)

if __name__ == '__main__':
    root_dir = 'scripts/'

    config = get_cfg_file_handle()

    container = config.get('NUTSHELL', 'container') == 'true'
    nutshell = config.get('NUTSHELL', 'nutshell') == 'true'

    output_filename = 'create-img-' + config.get('CUSTOMIZABLE', 'filename')[:-4] + '.sh'
    if nutshell:
        output_filename = 'create-img-' + config.get('NUTSHELL', 'filename')[:-4] + '.sh'

    create_output_file()

    # Write head script
    filename = config.get('SCRIPT_FILE_NAMES', 'head_script')
    append_file_to_output(root_dir + filename)

    # Write script variables (defined in the configuration file)
    append_str_to_output('# Section: variables from configuration file\n\n')

    append_str_to_output('# The name and size of the image file '\
            'that will be generated.\n')
   
    if nutshell:
        append_str_to_output('FILENAME=' + config.get('NUTSHELL','filename') + '\n')
        append_str_to_output('CONT_FILENAME=' + config.get('CUSTOMIZABLE','filename') + '\n')
        append_str_to_output('FILESIZE=' + config.get('NUTSHELL', 'filesize') + '\n\n')
        append_str_to_output('HOST=' + config.get('NUTSHELL', 'hostname') + '\n')
        append_str_to_output('DEBIAN_DIST=' + config.get('NUTSHELL', 'ubuntu_dist') + '\n')
        append_str_to_output('DEBIAN_MIRROR=' + config.get('NUTSHELL', 'ubuntu_mirror') + '\n\n')
        append_str_to_output('CREATE_CONT=' + config.get('NUTSHELL', 'container') + '\n\n')
        append_str_to_output('CONPASS_TAR_PATH=' + config.get('NUTSHELL', 'conpaas_tar_path') + '\n\n')
        container = False;
    else:
        append_str_to_output('FILENAME=' + config.get('CUSTOMIZABLE', 'filename') + '\n')
        append_str_to_output('FILESIZE=' + config.get('CUSTOMIZABLE', 'filesize') + '\n\n')

        append_str_to_output('# The Debian distribution that you would '\
            'like to have installed (we recommend squeeze).\n')
        append_str_to_output('DEBIAN_DIST=' + config.get('RECOMMENDED', 'debian_dist') + '\n')
        append_str_to_output('DEBIAN_MIRROR=' + config.get('RECOMMENDED', 'debian_mirror') + '\n\n')

        append_str_to_output('# The architecture and kernel version for '\
            'the OS that will be installed (please make\n')
        append_str_to_output('# sure to modify the kernel version name accordingly if you modify the architecture).\n')

    optimize = config.get('CUSTOMIZABLE', 'optimize')

    hypervisor = config.get('CUSTOMIZABLE', 'hypervisor')
    if hypervisor != 'kvm' and hypervisor != 'xen':
        error('Unknown hypervisor "%s".' % hypervisor)
    
    cloud = config.get('CUSTOMIZABLE', 'cloud')
    if cloud == 'opennebula' or cloud == 'vbox':
        pass
    elif cloud == 'ec2':
        if hypervisor != 'xen':
            print 'WARNING: Your choice of hypervisor is not compatible with Amazon EC2. Xen will be used instead.'
            hypervisor = 'xen'
    else:
        error('Unknown cloud "%s".' % cloud)

    if container:
        cloud = config.get('NUTSHELL', 'cloud')
    
    append_str_to_output('CLOUD=' + cloud + '\n')

    arch = config.get('RECOMMENDED', 'arch')
    if arch == 'i386':
        kernel_arch = '686'   # yes not 'i386'
    elif arch == 'amd64':
        kernel_arch = 'amd64'
    else:
        error('Unknown arch "%s".' % arch)
    append_str_to_output('ARCH=%s\n' % arch)
    
    debian_dist = config.get('RECOMMENDED', 'debian_dist')
    if debian_dist == 'squeeze':
        if hypervisor == 'kvm':
            kernel_version = 'linux-image-%s' % kernel_arch
        elif hypervisor == 'xen':
            kernel_version = 'linux-image-xen-%s' % kernel_arch
    elif debian_dist == 'wheezy':
        # Debian wheezy use the same kernel image both for kvm and xen
        kernel_version = 'linux-image-%s' % kernel_arch
    else:
        error('Unknown Debian distribution "%s".' % debian_dist)
    
    if nutshell:
       append_str_to_output('OPTIMIZE=' + config.get('CUSTOMIZABLE', 'optimize') + '\n')
       if hypervisor == 'kvm':
           kernel_version = config.get('NUTSHELL', 'kvm_ubuntu_kernel_version')
       elif hypervisor == 'xen':
           kernel_version = config.get('NUTSHELL', 'xen_ubuntu_kernel_version')    

    append_str_to_output('KERNEL=%s\n' % kernel_version)
    
    append_str_to_output('\n\n')


    # Write message about the selected services
    print 'Setting up image for %s, with services:' % hypervisor.upper(),

    # Write general scripts
    #filenames = config.get('SCRIPT_FILE_NAMES', 'general_scripts')
    #for filename in filenames.split():
    #    append_file_to_output(root_dir + filename)
   
    if nutshell:
        filename = config.get('SCRIPT_FILE_NAMES', 'image_script_nutshell')
    elif container:
        filename = config.get('SCRIPT_FILE_NAMES', 'image_script_container')
    else:
        filename = config.get('SCRIPT_FILE_NAMES', 'image_script')

    append_file_to_output(root_dir + filename)    

    if nutshell:
        filenames = config.get('SCRIPT_FILE_NAMES', 'nutshell_config_scripts')
        for filename in filenames.split():
                        append_str_to_output("#Section " + filename + "\n\n")
                        append_file_to_output(root_dir + filename)
    else:

        filename = config.get('SCRIPT_FILE_NAMES', 'conpaas_core_script')
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

        if rm_script_args == '':
            rm_script_args = ' --none'

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


    suffix = '_nushell' if nutshell else ''
 
    # Write contextualization script
    if cloud == 'opennebula':
        filename = config.get('SCRIPT_FILE_NAMES', 'opennebula_script'+suffix)
    elif cloud == 'ec2':
        filename = config.get('SCRIPT_FILE_NAMES', 'ec2_script'+suffix)
    elif cloud == 'openstack':
       filename = config.get('SCRIPT_FILE_NAMES', 'ec2_script') 
    elif cloud == 'vbox':
        filename = config.get('SCRIPT_FILE_NAMES', 'vbox_script'+suffix)
    append_file_to_output(root_dir + filename)

    if not nutshell:
        if optimize == 'true':
            if container:
                filename = config.get('SCRIPT_FILE_NAMES', 'resize_container_script')
            else:
                filename = config.get('SCRIPT_FILE_NAMES', 'resize_script')
            append_file_to_output(root_dir + filename)   


    close_output_file()
   
    print "\nPlease run " +output_filename+ " as root"
  
