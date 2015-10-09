# #!/usr/bin/env python
# import pxssh
# import sys
# import time

# import paramiko
# # from config import config_parser
# class RemoteConnection:
    
#     def __init__(self, environ_vars = {}):
#         self.env_vars = environ_vars
#         paramiko.util.log_to_file('/tmp/am_ssh.log') 
    
#     # def run(self, host, cmd = None, script = None, user = config_parser.get("main", "agent_user")):
#     def run(self, host, cmd = None, script = None, user='root'):
# 		#output = None
# 		ssh = paramiko.SSHClient()
# 		ssh.load_system_host_keys()
# 		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 		tries = 3;
# 		#print "Connecting to ", host 
# 		while(tries > 0):
# 			try:
# 				# ssh.connect(host, username = user, password = config_parser.get("main", "agent_password"))
# 				ssh.connect(host, username = user, password = 'contrail')
# 				print "Success"
# 				break;
# 			except:
# 				tries = tries - 1;
# 				print "Failed connecting to %s, try connecting later..." % host
# 				time.sleep(10)
# 		if tries == 0:
# 			raise Exception("couldn't connect to ",host)
			
# 		cmd_to_execute = ";".join(["export %s='%s'" % (key, self.env_vars[key]) for key in self.env_vars])
# 		if cmd != None:
# 			cmd_to_execute = cmd_to_execute + ";" + cmd
# 		else:
# 			f = script.split("/")[-1]
# 			cmd_to_execute = cmd_to_execute + ";" + ";".join(["curl -O %s" % script, "chmod +x %s" % f, ". %s" % f])
# 		cmd_to_execute = cmd_to_execute.strip(";")
# 		#print "Executing :", cmd_to_execute, " on ", host
# 		ssh_stdin, ssh_stdout, ssh_stderr = ssh.exec_command(cmd_to_execute)
# 		output = "\nERROR: ["
# 		output += ssh_stderr.read()
# 		output += "]"
# 		exit_status = ssh_stdout.channel.recv_exit_status()
# 		ssh.close()
# 		del ssh

# 		return exit_status, output

# if __name__ == "__main__":
# 	remote = RemoteConnection()
# 	hosts = ['root@10.180.8.1','root@10.180.8.2']
# 	remote.do_run(hosts, [['ls'],['ls -l']])

