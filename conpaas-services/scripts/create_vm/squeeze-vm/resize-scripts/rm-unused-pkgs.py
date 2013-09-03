#!/usr/bin/python

from subprocess import Popen
from subprocess import PIPE
import re
import sys

# Define which are the 'root' packages (form
# which the dependency analysis starts)


debian_pkgs = ['linux-image-2.6.32-5-xen-amd64', 'linux-image-2.6.32-5-amd64', 
               'initramfs-tools', 'bash', 'apt', 'apt-utils', 'cron', 
               'vim-tiny', 'grub-common', 'grub', 'grub-pc', 'net-tools', 
               'iputils-ping', 'rsyslog', 'binfmt-support', 'dbus', 
               'avahi-daemon', 'libavahi-core7', 'libdaemon0', 'libnss-mdns', 
               'bsdmainutils', 'resolvconf', 'netbase', 'iproute', 'ifupdown',
               'isc-dhcp-common', 'isc-dhcp-client']

core_pkgs = ['openssh-server', 'python', 'python-pycurl', 'python-openssl',
             'python-m2crypto', 'python-cheetah', 'libxslt1-dev', 'yaws',
             'subversion', 'unzip', 'less', 'ipop',
             'ganglia-monitor', 'gmetad', 'rrdtool', 'logtail', 'python-netaddr']

php_pkgs = ['php5-fpm', 'php5-curl', 'php5-mcrypt', 'php5-mysql', 'php5-odbc',
            'php5-pgsql', 'php5-sqlite', 'php5-sybase', 'php5-xmlrpc',
            'php5-xsl', 'php5-adodb', 'php5-memcache', 'php5-gd', 'nginx',
            'git', 'tomcat6-user', 'memcached','python-scipy',
            'libatlas-base-dev', 'libatlas3gf-base', 'python-dev', 'python-setuptools']

mysql_pkgs = ['mysql-server', 'python-mysqldb']

condor_pkgs = ['sun-java6-jdk', 'ant', 'condor']

selenium_pkgs = ['iceweasel', 'xvfb', 'xinit', 'google-chrome-stable']

hadoop_pkgs =   ['hadoop-0.20', 'hadoop-0.20-namenode', 'hadoop-0.20-datanode',
                'hadoop-0.20-secondarynamenode', 'hadoop-0.20-jobtracker',
                'hadoop-0.20-tasktracker', 'hadoop-pig', 'hue-common',
                'hue-filebrowser', 'hue-jobbrowser', 'hue-jobsub',
                'hue-plugins', 'hue-server', 'dnsutils']

scalaris_pkgs = ['scalaris', 'screen', 'erlang']

xtreemfs_pkgs = ['xtreemfs-server', 'xtreemfs-client', 'xtreemfs-tools']

cds_pkgs = ['php5-fpm', 'php5-curl', 'php5-mcrypt', 'php5-mysql', 'php5-odbc',
            'php5-pgsql', 'php5-sqlite', 'php5-sybase', 'php5-xmlrpc',
            'php5-xsl', 'php5-adodb', 'php5-memcache', 'php5-gd git',
            'tomcat6-user', 'memcached',
            'libpcre3-dev', 'libssl-dev', 'libgeoip-dev', 'libperl-dev']


# Execute shell command
def shell_cmd(cmd):
    return Popen(cmd, stdout=PIPE, shell=True).stdout.read()

# Take the output of a shell command and return a list
# of tokens from it
def string_to_list(s):
    # Normalize whitespace to single spaces
    s = re.sub(r'\s+', ' ', s);
    return s.split()

def write_to_file(filename, data):
	f = open(filename, 'w')
	print >> f, data
	f.close()

def remove_pkg(pkg):
    return shell_cmd("apt-get -y purge %s 2>&1 " % pkg)

def force_remove_pkg(pkg):
    return shell_cmd("echo 'Yes, do as I say!' | apt-get -y --force-yes purge %s 2>&1 " % pkg)

def doublecheck_unneeded_pkgs(unneeded_pkgs):
    to_keep = []
    to_remove = []
    to_remove_with_wornings = []
    for pkg in unneeded_pkgs:
        output = shell_cmd('apt-get -s purge %s ' % pkg)
        warn = re.findall(r'WARNING: The following essential packages will be removed.', output)

        output = re.findall(r'The following packages will be REMOVED:(.*?)^\S', output, re.S | re.M)

        l = len(output)
        if l == 0:
            print  '%s does not have a remove list' % pkg
            continue

        if l > 1:
            sys.exit('Error: More than one list of packages to be removed.')

        # Unpack from list
        output = output[0]
        # Remove '*' chars
        output = re.sub(r'\*', '', output);
        output = string_to_list(output)
        output = set(output)

        if len(output.intersection(needed_pkgs)) > 0:
            to_keep.append(pkg)
        else:
            if warn:
                to_remove_with_wornings.append(pkg)
            else:
                to_remove.append(pkg)

    return to_keep, to_remove, to_remove_with_wornings


# Necessary packages
args = sys.argv[1:]
pkgs = []
pkgs.extend(debian_pkgs)
pkgs.extend(core_pkgs)

if len(args) == 0:
    sys.exit('The script needs at least one of the arguments: '
    '--all, --none, --php, --mysql, --condor, --selenium, --hadoop, --scalaris, --xtreemfs, --cds, --debug.')

if '--debug' in args:
	dbg = True
	args.remove('--debug')
else:
	dbg = False

if '--all' in args:
    pkgs.extend(php_pkgs)
    pkgs.extend(mysql_pkgs)
    pkgs.extend(condor_pkgs)
    pkgs.extend(selenium_pkgs)
    pkgs.extend(hadoop_pkgs)
    pkgs.extend(scalaris_pkgs)
    pkgs.extend(xtreemfs_pkgs)
    pkgs.extend(cds_pkgs)
    args.remove('--all')
elif '--none' in args:
    args.remove('--none')
else:
    if '--php' in args:
        pkgs.extend(php_pkgs)
        args.remove('--php')
    if '--mysql' in args:
        pkgs.extend(mysql_pkgs)
        args.remove('--mysql')
    if '--condor' in args:
        pkgs.extend(condor_pkgs)
        args.remove('--condor')
    if '--selenium' in args:
        pkgs.extend(selenium_pkgs)
        args.remove('--selenium')
    if '--hadoop' in args:
        pkgs.extend(hadoop_pkgs)
        args.remove('--hadoop')
    if '--scalaris' in args:
        pkgs.extend(scalaris_pkgs)
        args.remove('--scalaris')
    if '--xtreemfs' in args:
        pkgs.extend(xtreemfs_pkgs)
        args.remove('--xtreemfs')
    if '--cds' in args:
        pkgs.extend(cds_pkgs)
        args.remove('--cds')

if args:
    sys.exit('Error: Unrecognized or duplicate arguments: %s' % str(args))

# Install apt-rdepends
print shell_cmd('apt-get -y install apt-rdepends 2>&1 ')

# Make a list of needed packages
needed_pkgs = set([])
for pkg in pkgs:
    print 'Processing ' + pkg
    needed_pkgs.add(pkg)
    dependencies = shell_cmd('apt-rdepends %s 2>&1 | awk -F"Depends:|PreDepends:" \'/Depends: / || /PreDepends: / { print $2 }\' | awk \'{print $1}\'| sort -u' % pkg)

    needed_pkgs.update(string_to_list(dependencies))

needed_pkgs = list(needed_pkgs)
needed_pkgs.sort()
needed_pkgs = set(needed_pkgs)

if (dbg):
    write_to_file('needed_pkgs', needed_pkgs)

# Useful
# shell_cmd("dpkg-query -Wf '${Installed-Size}\t\t${Package}\t\t${Priority}\n' | sort -u")

# Make a list of installed packages
installed_pkgs = shell_cmd("dpkg-query -Wf '${Package}\n' | sort -u")
installed_pkgs = string_to_list(installed_pkgs)
installed_pkgs = set(installed_pkgs)

if (dbg):
    write_to_file('installed_pkgs', installed_pkgs)

# Find unneeded packages
unneeded_pkgs = installed_pkgs.difference(needed_pkgs)
weird_pkgs = needed_pkgs.difference(installed_pkgs)

# Some of the packages in unneeded_pkgs can still be required
to_keep, to_remove, to_remove_with_wornings = \
    doublecheck_unneeded_pkgs(unneeded_pkgs)
needed_pkgs.update(to_keep)
unneeded_pkgs = to_remove + to_remove_with_wornings

if (dbg):
    write_to_file('to_remove', to_remove)
    write_to_file('to_remove_with_wornings', to_remove_with_wornings)


print "REMOVING PACKAGES ..."
for p in to_remove:
	print remove_pkg(p), "\n"
print shell_cmd('apt-get -y autoremove 2>&1')

# Free additional space
#apt-get -y install localepurge
#localepurge
#apt-get -y purge localepurge

print shell_cmd('rm -rf /usr/share/doc/ 2>&1')
print shell_cmd('rm -rf /usr/share/doc-base/ 2>&1')
print shell_cmd('rm -rf /usr/share/man/ 2>&1')

