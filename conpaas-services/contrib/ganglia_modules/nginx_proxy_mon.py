# Ganglia module for parsing the nginx proxy access log.
# Computes average request rate and response time for static and php requests.
# Uses the logtail tool to access the log.
import subprocess, threading;
import time, os;
import logging;

web_proxy_log = '/var/cache/cpsagent/nginx-proxy-timed.log'
dbg_log = '/tmp/nginx_proxy_dbg.log'
logtail_interval = 15
descriptors = []

logger = logging.getLogger('Ganglia nginx proxy')

# These variables hold the computed monitoring results.
web_response_time_lb = 0
web_request_rate_lb = 0

php_response_time_lb = 0
php_request_rate_lb = 0

# Can be used to stop the parsing thread.
stop_parsing = False

# A separate thread that checks what has been added to the log,
# at regular time intervals. It computes the response time
# and request rate for the last time interval and stores them
# in the global variables.
class NginxLogParser(threading.Thread):
	def __init__(self, proxy_log_file, parse_interval):
		global logger

		threading.Thread.__init__(self)

		self.proxy_log_file = proxy_log_file
		self.parse_interval = parse_interval

		logger.debug("Initializing NginxLogParser with parse interval: " + \
			str(self.parse_interval) + ", proxy log: " + self.proxy_log_file)	
		self.tmp_proxy_file = '/tmp/nginx_proxy_temp.log'

		# last timestamp seen in the log
		self.last_access_time = 0

	# Reads the lines that have been written in the log since the last access.
	# Computes the average request rate and response time and writes them
	# in global variables.
	def process_proxy_log(self):  
		global logger, web_response_time_lb, web_request_rate_lb, php_response_time_lb, php_request_rate_lb

		logger.debug("Processing proxy log...")

		try:
			# get what has been added to the log since last time we checked
			f_tmp_w = open(self.tmp_proxy_file, 'w')
			subprocess.call(['/usr/sbin/logtail', '-f', self.proxy_log_file], stdout=f_tmp_w)
			f_tmp_w.close()

			start_time = 0
			crt_time = self.last_access_time
			n_web_requests = 0
			n_php_requests = 0
			total_web_resp_time = 0
			total_php_resp_time = 0
		
			f_tmp_r = open(self.tmp_proxy_file, 'r')
			for line in f_tmp_r:
				logger.debug(line + '\n')
				tokens = line.split()
				nt = len(tokens)
				crt_time = float(tokens[nt - 2])
				if (start_time == 0):
					start_time = crt_time
				
				if (line.find('php') >= 0):
					total_php_resp_time += float(tokens[nt - 1])	
					n_php_requests += 1
				else:
					total_web_resp_time += float(tokens[nt - 1])	
					n_web_requests += 1

			# not the first time we read from the log
			if (self.last_access_time != 0):
				start_time = self.last_access_time
		
			end_time = crt_time

			# request rate in requests / sec
			if (start_time != end_time):
				web_request_rate_lb = n_web_requests / (end_time - start_time)
				php_request_rate_lb = n_php_requests / (end_time - start_time) 
				self.last_access_time = end_time
			else:
				web_request_rate_lb = 0
				php_request_rate_lb = 0

			logger.debug("Start time: " + str(start_time) + ", end time: " + str(end_time) + "\n")
			# response time in ms
			if ((n_web_requests != 0) and (start_time != end_time)):
				web_response_time_lb = (total_web_resp_time * 1000) / n_web_requests			
			else:
				web_response_time_lb = 0
			
			if ((n_php_requests != 0) and (start_time != end_time)):
				php_response_time_lb = (total_php_resp_time * 1000) / n_php_requests			
			else:
				php_response_time_lb = 0

			logger.debug("Web req rate: " + str(web_request_rate_lb) + ", web response time: " + \
									str(web_response_time_lb) + "n. web requests: " + str(n_web_requests) + "\n")
			logger.debug("PHP req rate: " + str(php_request_rate_lb) + ", php response time: " + \
									str(php_response_time_lb) + "n. php requests: " + str(n_php_requests) + "\n")
			
			f_tmp_r.close()

		except Exception, ex:
			logger.exception(ex)
			return 1 		

		return 0

	def run(self):
		logger.info("Started web log parsing thread...")
		while True:		
			logger.debug("Processing web log...")
			self.process_proxy_log()
			logger.debug("Going to sleep for: " + str(self.parse_interval))

			if stop_parsing:
				break

			time.sleep(self.parse_interval)			


def web_request_rate_lb_handler(name):
	global web_request_rate_lb
	return web_request_rate_lb

def web_response_time_lb_handler(name):
	global web_response_time_lb
	return web_response_time_lb

def php_request_rate_lb_handler(name):
	global php_request_rate_lb
	return php_request_rate_lb

def php_response_time_lb_handler(name):
	global php_response_time_lb
	return php_response_time_lb

def metric_init(params):
	global descriptors, web_proxy_log, logtail_interval
	global logger

	logging.basicConfig(
		filename='/tmp/ganglia_modules.log',
		format='%(asctime)-6s: %(name)s - %(levelname)s - %(message)s')
	logger.setLevel(logging.INFO)

	logger.info("Initializing metrics...")

	if 'proxy_log' in params:
		web_proxy_log = params['proxy_log']
	if 'monitor_interval' in params:
		logtail_interval = int(params['monitor_interval'])

	d1 = {'name': 'web_request_rate_lb',
      	'call_back': web_request_rate_lb_handler,
       	'time_max': 90,
       	'value_type': 'float',
       	'units': 'req/s',
       	'slope': 'both',
       	'format': '%f',
       	'description': 'Load Balancer Web Request Rate',
       	'groups': 'web'}

	d2 = {'name': 'web_response_time_lb',
		'call_back': web_response_time_lb_handler,
		'time_max': 90,
		'value_type': 'float',
		'units': 'ms',
		'slope': 'both',
		'format': '%f',
		'description': 'Load Balancer Web Response Time',
		'groups': 'web'}

	d3 = {'name': 'php_request_rate_lb',
      	'call_back': php_request_rate_lb_handler,
       	'time_max': 90,
       	'value_type': 'float',
       	'units': 'req/s',
       	'slope': 'both',
       	'format': '%f',
       	'description': 'Load Balancer PHP Request Rate',
       	'groups': 'web'}

	d4 = {'name': 'php_response_time_lb',
		'call_back': php_response_time_lb_handler,
		'time_max': 90,
		'value_type': 'float',
		'units': 'ms',
		'slope': 'both',
		'format': '%f',
		'description': 'Load Balancer PHP Response Time',
		'groups': 'web'}

	
	descriptors = [d1, d2, d3, d4]

	parser_thread =  NginxLogParser(web_proxy_log, logtail_interval)	
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
