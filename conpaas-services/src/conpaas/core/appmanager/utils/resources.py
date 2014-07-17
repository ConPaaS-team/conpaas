#!/usr/bin/env python
#import pxssh
import sys
import time
#import httplib2


def get_utilization(machines):
    util_data = []
    return util_data


class RemoteConnection:
    
    def __init__(self, devicetype = "VM", environ_vars = {}):
        """
            Constructor.
            Uses Paramiko   
            Connection protocol is different depending on the resource type we are trying to connect to
        """
        self.type = devicetype 
        self.env_vars = environ_vars
        
    def run(self, host, cmd = None, script = None, user = "root"):
        return "OK"
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        tries = 3;
        print "Connecting to ", host 
        while(tries > 0):
            try:	
                ssh.connect(host, username = user)
                print "Success"
                break;
            except:
                tries = tries - 1;
                print "Try connecting later..."
            time.sleep(10)
        if tries == 0:
            return None
        cmd_to_execute = ";".join(["export %s=%s" % (key, self.env_vars[key]) for key in self.env_vars])
        if cmd != None:
            cmd_to_execute = cmd_to_execute + ";" + cmd
        else:
            f = script.split("/")[-1]
            cmd_to_execute = cmd_to_execute + ";" + ";".join(["wget %s" % script, "chmod +x %s" % f, ". %s" % f])
        cmd_to_execute = cmd_to_execute.strip(";")
            
        print "Executing :", cmd_to_execute, " on ", host
        ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
        output = ssh_stdout.read()

        exit_status = ssh_stdout.channel.recv_exit_status()
        ssh.close()
        del ssh

        return output



