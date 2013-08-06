# Ganglia module for parsing the provisioning log.
# Computes average request rate and response time for static and php requests.
# Uses the logtail tool to access the log.
import subprocess, threading;
import time, os;
import logging;
import datetime
import pickle

provisioning_log = '/tmp/provisioning.log'
#provisioning_log = '/Users/asturias/proof_log.log'
dbg_log = '/tmp/provisioning_dbg.log'
logtail_interval = 90
STORAGE_NUM_MACHINES = '/tmp/num_machines.pickle'
#logtail_interval = 420
descriptors = []

logger = logging.getLogger('Ganglia Num. machines provisioning')

# These variables hold the computed monitoring results.
num_machines_lb = 2

# Can be used to stop the parsing thread.
stop_parsing = False

# A separate thread that checks what has been added to the log,
# at regular time intervals. It computes the number of machines provisioned any given time
# and stores them in the global variable.
class ProvisioningLogParser(threading.Thread):
	def __init__(self, provisioning_log_file, parse_interval):
		global logger

		threading.Thread.__init__(self)

		self.provisioning_log_file = provisioning_log_file
		self.parse_interval = parse_interval

		logger.info("Initializing ProvisioningLogParser with parse interval: " + \
			str(self.parse_interval) + ", provisioning log: " + self.provisioning_log_file)	
		self.tmp_provisioning_file = '/tmp/provisioning_temp.log'

		# last timestamp seen in the log
		self.last_access_time = 0

	# Reads the lines that have been written in the log since the last access.
	# Computes the number of machines provisioned to the application
	# in global variables.
	def process_provisioning_log(self):  
		global logger, num_machines_lb

		logger.info("Processing provisioning log...")

		try:
			
			# get what has been added to the log since last time we checked
			f_tmp_w = open(self.tmp_provisioning_file, 'w')
			subprocess.call(['/usr/sbin/logtail', '-f', self.provisioning_log_file], stdout=f_tmp_w)
			f_tmp_w.close()

			start_time = 0
			crt_time = self.last_access_time
			n_machines = 0
			
			total_machines = []
			# We add the manager itself.
			total_machines.append('localhost')
			
			#### Aspect of the provisioning.log file #####
			#  Updating nodes information from ConPaaS manager
			#  __main__ RRD file not found:
			#  update_VM_Usage: adding one machine to the cost_aware system.
			#  **** Web monitoring data: *****
			#  Getting proxy monitoring info for
			#  Getting web monitoring info for
			#  Getting backend monitoring info for
			#  Autoscaling Monitoring data was not properly retrieved, will retry later.
			##############################################
		
			f_tmp_r = open(self.tmp_provisioning_file, 'r')

			machines = {}

			for line in f_tmp_r:
				logger.info(line + '\n')
				if "Getting proxy monitoring info for" in line:
					tokens = line.split()
					nt = len(tokens)
					logger.info(tokens[nt - 2])
					if not tokens[nt - 2] in total_machines:
						total_machines.append(tokens[nt - 2])
				
				if "Getting web monitoring info for" in line:
					tokens = line.split()
					nt = len(tokens)
					logger.info(tokens[nt - 2])
					if not tokens[nt - 2] in total_machines:
						total_machines.append(tokens[nt - 2])
				
				if "Getting backend monitoring info for" in line:
					tokens = line.split()
					nt = len(tokens)
					logger.info(tokens[nt - 2])
					if not tokens[nt - 2] in total_machines:
						total_machines.append(tokens[nt - 2])
				
				if "**** Web monitoring data: *****" in line or "Autoscaling Monitoring data was not properly retrieved, will retry later." in line:
					break
				
				if "update_vm_usage: adding one machine to the cost_aware system." in line:
					tokens = line.split()
					nt = len(tokens)
					
					inst_type = tokens[nt - 1]
					ip = tokens[nt - 6]
					
					logger.info('IP:'+str(ip)+' inst_type: '+str(inst_type)+' Num. machines:' +str(len(total_machines))+'\n')
					machines[ip]= inst_type
					
					time = tokens[nt - 17]
					date = tokens[nt - 18]

					d = datetime.datetime(int(date[:4]), int(date[6:7]), int(date[9:10]), int(time[:2]), int(time[4:5]), int(time[6:7]), int(time[9:]))
					crt_time = float(d.strftime('%s'))
					if (start_time == 0):
						start_time = crt_time

			# not the first time we read from the log
			if (self.last_access_time != 0):
				start_time = self.last_access_time
		
			end_time = crt_time

			# User current number of machines and store it 
			if len(total_machines) > 1:
				num_machines_lb = len(total_machines)
				f = open(STORAGE_NUM_MACHINES,'wb')
				pickle.dump(num_machines_lb, f)
			
			# Recover previous value
			elif os.path.exists(STORAGE_NUM_MACHINES):
			    f=open(STORAGE_NUM_MACHINES,'rb')
			    num_machines_lb = pickle.load(f)
			    
				 
			self.last_access_time = end_time

			logger.info("Start time: " + str(start_time) + ", end time: " + str(end_time) + "\n")
	
			logger.info("Num machines: " + str(num_machines_lb) + ", Machines: " + \
									str(machines) + "\n")
			
			f_tmp_r.close()

		except Exception as  ex:
			logger.info(ex)
			return 1 		

		return 0

	def run(self):
		logger.info("Started provisioning log parsing thread...")
		while True:		
			logger.info("Processing provisioning log...")
			self.process_provisioning_log()
			logger.info("Going to sleep for: " + str(self.parse_interval))

			if stop_parsing:
				break

			time.sleep(self.parse_interval)			


def num_machines_lb_handler(name):
	global num_machines_lb
	return num_machines_lb

def metric_init(params):
	global descriptors, provisioning_log, logtail_interval
	global logger

	logging.basicConfig(
		filename='/tmp/ganglia_modules.log',
		format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
	logger.setLevel(logging.INFO)

	logger.info("Initializing metrics...")

	if 'provisioning_log' in params:
		provisioning_log = params['provisioning_log']
	if 'monitor_interval' in params:
		logtail_interval = int(params['monitor_interval'])


	d1 = {'name': 'num_machines_lb',
		'call_back': num_machines_lb_handler,
		'time_max': 420,
		'value_type': 'float',
		'units': '',
		'slope': 'both',
		'format': '%f',
		'description': 'Num. Machines',
		'groups': 'Autoscaling'}

	
	descriptors = [d1]

	parser_thread =  ProvisioningLogParser(provisioning_log, logtail_interval)	
	parser_thread.start()
	return descriptors

def metric_cleanup():
	'''Clean up the metric module.'''
	global stop_parsing

	stop_parsing = True

#This code is for debugging and unit testing
if __name__ == '__main__':	
	metric_init({})
	time.sleep(5)
	for d in descriptors:
		v = d['call_back'](d['name'])
		print 'value for %s is %f' % (d['name'],  v)

	stop_parsing = True
