# -*- coding: utf-8 -*-

"""
    :copyright: (C) 2010-2013 by Contrail Consortium.
"""

import os
import sys
import stat
import re
from functools import wraps
testing_submit = False

def test_rw_permissions(f):
	"""
	Checks the read/write permissions of the specified file
	"""
	@wraps(f)
	def rw_check(thefile, *args, **kwargs):
		if not os.access(thefile, os.R_OK | os.W_OK):
			raise Exception("Cannot read/write file %s " % thefile)
		else:
			return f(thefile, *args, **kwargs)
	return rw_check

@test_rw_permissions
def add_node_info(hostsfile, ip, vmid):
	"""
	Add the newly created agent-IP and VM-id to the hostsfile
	"""
	targetfile = open(hostsfile,'a')
	targetfile.write("%s	worker-%s.htc\n" % (ip, vmid))
	targetfile.close()

@test_rw_permissions
def remove_node_info(hostsfile, ip):
	"""
	Remove the agent-IP and VM-id from the hostsfile
	"""
	contentlines = open(hostsfile).readlines()
	targetfile = open(hostsfile, 'w')
	for line in contentlines:
		if not re.search('^' + ip, line):
			targetfile.write(line)

def submit_a_task(jobnr, bagnr, tasknr, commandline, workerlist, thedict={}):
        # print >> sys.stderr, 'tesing_subnit = %s' % testing_submit
        setup_dict = dict(
                Universe = 'vanilla' ,
                Log = 'htc.$(Cluster).$(Process).log' ,
                Output = 'htc.$(Cluster).$(Process).out' ,
                Error = 'htc.$(Cluster).$(Process).err' ,
                should_transfer_files = 'YES' ,
                when_to_transfer_output = 'ON_EXIT' ,
                HtcJob = jobnr ,
                HtcBag = bagnr,
                HtcTask = tasknr     # should be tasknr from original file
        )
        command = commandline.split(' ')
        farm_dir = "/var/lib/condor/taskfarm"
        if not os.path.isdir(farm_dir):
		os.system("sudo -u condor mkdir -p %s" % farm_dir)
                # os.makedirs(farm_dir, 0777)
        os.chdir(farm_dir)
        if command[0] == "java":
            setup_dict["Universe"] = 'java'
            classpath = ''
            if command[1] == '-cp':
                classpath = command[2]+ "/"
            exe = open(classpath + command[3]+".class").read()
            open(command[3]+".class", 'w').write(exe)
            setup_dict['executable'] = command[3]+".class"
            setup_dict['arguments'] = ''
            for i in range(3,len(command)):
                setup_dict['arguments'] = setup_dict['arguments'] + command[i] + " "
            setup_dict['transfer_input_files'] = ''
            classes = os.listdir(classpath)
            print >> sys.stderr, classes
            for a_class in classes:
                if a_class.endswith(".class"):
                    exe = open(classpath + a_class).read()
                    open(a_class, 'w').write(exe)
                    if setup_dict['transfer_input_files'] == '':
                        setup_dict['transfer_input_files'] =  a_class
                    else:
                        setup_dict['transfer_input_files'] = setup_dict['transfer_input_files'] + ',' + a_class
        # set up the task file
	base_filename = 'htc-j-%d-b-%d-t-%d' % (jobnr, bagnr, tasknr)
        print >> sys.stderr, 'submit_a_task ', base_filename, "\t'%s'\t" % commandline, workerlist
        thetask_file = '%s.thetask' % (base_filename)
        fd = open( thetask_file, "w" ) # or die("Cannot create %s: %s" % (filename, error_nr))
        fd.write( "#!/bin/bash\n%s\n" % commandline )
        fd.close()
        os.chmod( thetask_file, os.stat(thetask_file).st_mode | stat.S_IEXEC | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH )
        # set up the ClassAd submit file
        classad_file = '%s.classad' % (base_filename)
        fd = open( classad_file, "w" ) # or die("Cannot create %s: %s" % (filename, error_nr))
        if command[0] !=  'java':
                setup_dict['Cmd'] = thetask_file
        # setup_dict['ConpaasWorkerType'] = workertype
        # setup_dict['ConpaasSequenceNumber'] = tasknr
        for k, v in setup_dict.iteritems():
            if k[:3] == 'Htc':
                    fd.write( "+%s = %s\n" % (k, v) )
            else:
                    fd.write( "%s = %s\n" % (k, v) )
        for k, v in thedict.iteritems():
            fd.write( "%s = %s\n" % (k, v) )
        queued = False
        for w in workerlist:
                fd.write("Requirements = TARGET.CloudMachineType ==  \"%s\"\n" % w)
                fd.write( "queue 1\n\n" )
                queued = True
        if not queued:
                fd.write( "queue 1\n" )
        fd.close()
        if testing_submit:
                os.system("head -v -n 20 %s" % thetask_file)
                os.system("head -v -n 20 %s" % classad_file)
        command = "sudo -u condor condor_submit %s" % classad_file
        if testing_submit:
                command = "echo " + command
        else:
                os.system("echo " + command)
        os.system(command)
        return

if __name__ == "__main__":
        # testing_submit = True
        submit_a_task(0, 0, 1 , 
                "/bin/sleep 3 && echo \"hi 1\" >> file.txt",
                [ "small", "medium", "large" ],
                { 
			#'ConpaasUsage': "UsageFirst"
		}
                )
                
        submit_a_task(1, 3, 2 , 
                "/bin/sleep 5 && echo \"hi 5\" >> file.txt",
                [],
                { 
			#'ConpaasUsage': "UsageFirst"
		}
                )
                
