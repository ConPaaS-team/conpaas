# Ganglia module for parsing the PHP-FPM access log.
# Computes average request rate and response time.
# Uses the logtail tool to access the log.
import subprocess, threading;
import time, os;
import logging;

php_fpm_log = '/var/cache/cpsagent/fpm-access.log'
dbg_log = '/tmp/php_mon_dbg.log'
logtail_interval = 15
descriptors = []

logger = logging.getLogger('Ganglia PHP')

# These global variables hold the computed monitoring results
php_response_time = 0
php_request_rate = 0

# Can be used to stop the parsing thread
stop_parsing = False

# A separate thread that checks what has been added to the log,
# at regular time intervals. It computes the response time
# and request rate for the last time interval and stores them
# in the global variables. 
class PHPLogParser(threading.Thread):
	def __init__(self, php_log_file, parse_interval):
		global logger

		threading.Thread.__init__(self)

		self.log_file = php_log_file		
		self.parse_interval = parse_interval
		logger.debug("Initializing PHPLogParser with parse interval: " + \
			str(self.parse_interval) + ", log file: " + self.log_file)
		self.tmp_log_file = '/tmp/php_mon_temp.log'		

		# last timestamp seen in the log
		self.last_access_time = 0

	# Reads the lines that have been written in the log since the last access.
	# Computes the average request rate and response time and stores them
	# in global variables.
	def process_php_log(self):  
		global logger, php_response_time, php_request_rate

		logger.debug("Processing PHP log...")

		try:
			# get what has been written in the log since the last time we checked
			f_tmp_w = open(self.tmp_log_file, 'w')
			subprocess.call(['/usr/sbin/logtail', '-f', self.log_file], stdout=f_tmp_w)
			f_tmp_w.close()

			start_time = 0
			crt_time = self.last_access_time
			n_requests = 0
			total_resp_time = 0
		
			f_tmp_r = open(self.tmp_log_file, 'r')
			for line in f_tmp_r:
				logger.debug(line + '\n')
				tokens = line.split()
				nt = len(tokens)
				crt_time = float(tokens[nt - 2])
				if (start_time == 0):
					start_time = crt_time
				total_resp_time += float(tokens[nt - 1])	
				n_requests += 1

			# not the first time we read from the log
			if (self.last_access_time != 0):
				start_time = self.last_access_time
		
			end_time = crt_time

			logger.debug("Start time: " + str(start_time) + ", end time: " + str(end_time) + "\n")

			# request rate in requests / sec
			if (start_time != end_time):
				php_request_rate = n_requests / (end_time - start_time) 
				self.last_access_time = end_time
			else:
				php_request_rate = 0

			# response time in ms
			if (n_requests != 0):
				php_response_time = (total_resp_time) / n_requests			
			else:
				php_response_time = 0

			logger.debug("Req rate: " + str(php_request_rate) + ", response time: " + str(php_response_time) + 
"n. requests: " + str(n_requests) + "\n")

			f_tmp_r.close()

		except Exception, ex:
			logger.exception(ex)
			return 1 		

		return 0

	def run(self):
		logger.info("Started FPM log parsing thread...")
		while True:		
			logger.debug("Preparing to process log...")
			self.process_php_log()
			logger.debug("Going to sleep for: " + str(self.parse_interval))

			if stop_parsing:
				break

			time.sleep(self.parse_interval)			


def request_rate_handler(name):
	global php_request_rate
	return php_request_rate

def response_time_handler(name):
	global php_response_time
	return php_response_time

def metric_init(params):
	global descriptors, php_fpm_log, logtail_interval
	global logger

	logging.basicConfig(
		filename='/tmp/ganglia_modules.log',
		format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
	logger.setLevel(logging.INFO)

	logger.info("Initializing metrics...")

	if 'php_fpm_log' in params:
		php_fpm_log = params['php_fpm_log']
	if 'monitor_interval' in params:
		logtail_interval = int(params['monitor_interval'])

	d1 = {'name': 'php_request_rate',
      	'call_back': request_rate_handler,
       	'time_max': 90,
       	'value_type': 'float',
       	'units': 'req/s',
       	'slope': 'both',
       	'format': '%f',
       	'description': 'PHP Request Rate',
       	'groups': 'web'}

	d2 = {'name': 'php_response_time',
		'call_back': response_time_handler,
		'time_max': 90,
		'value_type': 'float',
		'units': 'ms',
		'slope': 'both',
		'format': '%f',
		'description': 'PHP Response Time',
		'groups': 'web'}

	descriptors = [d1, d2]

	parser_thread =  PHPLogParser(php_fpm_log, logtail_interval)	
	parser_thread.start()
	return descriptors

def metric_cleanup():
	'''Clean up the metric module.'''
	global stop_parsing

	stop_parsing = True

# This code is for debugging and unit testing
if __name__ == '__main__':
	metric_init({})
	time.sleep(5)
	for d in descriptors:
		v = d['call_back'](d['name'])
		print 'value for %s is %f' % (d['name'],  v)

	stop_parsing = True
