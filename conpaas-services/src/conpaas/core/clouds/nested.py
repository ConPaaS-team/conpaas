#from cpsdirector.common import log
import time

class NestedCloud():

    def __init__(self, **kwargs):
        self.cloud_name = kwargs['cloud_name']
        self.image_id = kwargs['image_id']
        self.size_id = kwargs['size_id']
        self.location_name = kwargs['location_name']
        self.vnet_id = kwargs['vnet_id']
        self.access_id = kwargs['access_id']
        self.secret_key = kwargs['secret_key']
        self.keyname = kwargs['keyname']
        self.security_group = kwargs['security_group']
        
        self.shared_pool = {}
        self.private_pool = {}
        self.node_index = 0
       
        self.private_pool['1'] = ['node']
                
    def _test_host(self, host, container_size):
        max_cpu = int(host['total']['cpu'])
        max_mem = int(host['total']['memory_mb'])
        new_cpu_usage = int(container_size.vcpus) + int(host['used_now']['cpu'])
        new_memory_usage = int(container_size.ram) + int(host['used_now']['memory_mb'])
    
        if new_cpu_usage > max_cpu or new_memory_usage > max_mem:
            return False

        return True 

    def _check_resources(self, hosts, size):
        for host_name in hosts:
            if self._test_host(hosts[host_name], size):
                return True
    
        return False

    def clean_shared_pool(self, driver, size):
        hosts = driver.list_compute_hosts()

        for host_name in hosts:
            if len(hosts[host_name]['servers']) == 0:
                driver.remove_compute_node[host_name]

        time.sleep(2)

        hosts = driver.list_compute_hosts()

        used_cpu = 0
        used_ram = 0
        max_cpu = 0
        max_ram = 0
        cpu_per_node = 0
        ram_per_node = 0
        min_no_migration = 100    
        delete_host = None
        
        for host_name in hosts:
            used_cpu += int(hosts[host_name]['used_now']['cpu'])
            used_ram += int(hosts[host_name]['used_now']['memory_mb'])
            max_cpu += int(hosts[host_name]['total']['cpu'])
            max_ram += int(hosts[host_name]['total']['memory_mb'])
            cpu_per_node = int(hosts[host_name]['total']['cpu'])
            cpu_per_node = int(hosts[host_name]['total']['memory_mb'])
            if min_no_migration < len(hosts[host_name]['servers']):
                min_no_migration = len(hosts[host_name]['server'])
                delete_host = host_name        
        
        if max_cpu - used_cpu >= 2*cpu_per_node and max_ram - used_ram >= 2*ram_per_node:
                for server in hosts[delete_host]:
                    for host_name in hosts:
                        if self._test_host(hosts[host_name], size):
                            driver.migrate(server['name'], host_name)
                            break
                
    def create_container(self, driver, kwargs, app_id, private=False):
        size = kwargs['size']
        hosts = driver.list_compute_hosts()
       
        designated_host = None
        if private:
            if not app_id in self.private_pool:
                #log("No private resources available")
                return
        
            for instance in self.private_pool[app_id]:
                host = driver.list_compute_hosts[instance.name]
                if self._test_host(host, size):
                    designated_host = instance.name
                    break
            
            if not designated_host:
                #log("No private compute VM available to deploy container")
                return
        else:
            if app_id in self.shared_pool:
                for host in self.shared_pool[app_id]:
                    if self._test_host(hosts[host_name], kwargs['size']):
                        designated_host = host_name
                        break
        
            if not designated_host:
                for host_name in hosts:
                    if self._test_host(hosts[host_name], kwargs['size']):
                        designated_host = host_name
                        if app_id in self.shared_pool:
                            self.shared_pool[app_id].append(host_name)
                        else:
                            self.shared_pool[app_id] = [host_name]

        kwargs['availability_zone'] = 'nova:%s' % designated_host

        if not self._check_resources(hosts, kwargs['size']):
            #log("no more compute resources available")
            #driver.add_compute_node("node%d" % node_index)
            node_index += 1   
            
        return None
    
    def get_script(self, hostname):
        cloud_script = 'HOSTNAME=testnode\n' \
                        + 'echo "127.0.0.1\tlocalhost" > /etc/hosts\n' \
                        + 'echo "127.0.0.1\tcomp1" > /etc/hosts\n' \
                        + 'echo "172.16.0.210\ttest" >> /etc/hosts\n' \
                        + 'echo "172.16.0.219\tip-172-30-0-210.ec2.internal" >> /etc/hosts\n' \
                        + 'echo "172.16.0.219\tip-172-30-0-210" >> /etc/hosts\n' \
                        + 'echo \'{ ' \
                        + '\t"ip4": "172.16.0.251",\n' \
                        + '\t"xmpp_username": "useripop@gmail.com",\n' \
                        + '\t"xmpp_host": "talk.google.com",\n' \
                        + '\t"xmpp_password": "Ipop1234.",\n' \
                        + '\t"switchmode": 1,\n' \
                        + '\t"icc": true,\n' \
                        + '\t"bridge_ip": "172.16.0.4",\n' \
                        + '\t"icc_port": 30000}\' > /home/stack/kj/config.json\n' \
                        + 'cd /home/stack/kj\n' \
                        + './run.sh\n' \
                        + 'echo \'HOST_IP=127.0.0.1\n' \
                        + 'SERVICE_HOST=172.16.0.210\n' \
                        + 'ADMIN_PASSWORD=password\n' \
                        + 'MYSQL_PASSWORD=password\n' \
                        + 'RABBIT_PASSWORD=password\n' \
                        + 'SERVICE_PASSWORD=password\n' \
                        + 'SERVICE_TOKEN=tokentoken\n' \
                        + 'FLAT_INTERFACE=ipop\n' \
                        + 'FIXED_RANGE=172.16.0.0/24\n' \
                        + 'FIXED_NETWORK_SIZE=126\n' \
                        + 'FLOATING_RANGE=172.16.0.128/25\n' \
                        + 'MULTI_HOST=1\n' \
                        + 'LOGFILE=/opt/stack/logs/stack.sh.log\n' \
                        + 'SCREEN_LOGDIR=/opt/stack/logs\n' \
                        + 'DATABASE_TYPE=mysql\n' \
                        + 'MYSQL_HOST=$SERVICE_HOST\n' \
                        + 'RABBIT_HOST=$SERVICE_HOST\n' \
                        + 'GLANCE_HOSTPORT=$SERVICE_HOST:9292\n' \
                        + 'Q_HOST=$SERVICE_HOST\n' \
                        + 'ENABLED_SERVICES=n-cpu,n-net,rabbit,n-api \' > /home/stack/devstack/localrc \n' \
                        + 'cd /home/stack/devstack/\n' \
                        + 'sleep 40\n' \
                        + 'sudo -u stack FORCE=yes ./stack.sh\n' \
                        + 'sleep 20'
        
        return cloud_script            
    
    def generate_context(self, name):
        if self.cloud_name == 'OpenNebula':
            start_script = self.get_script(name).encode("hex")
            context_vars = {}
            context_vars['HOSTNAME'] = "comp1"
            context_vars['DNS'] = "$NETWORK[DNS,     NETWORK_ID=1]"
            context_vars['GATEWAY'] = "$NETWORK[GATEWAY, NETWORK_ID=1]"
            context_vars['NETMASK'] = "$NETWORK[NETMASK, NETWORK_ID=1]"
            context_vars['IP_PRIVATE'] = "$NIC[IP, NETWORK_ID=1]"
           
            context_vars['USERDATA'] = '23212f62696e2f626173680a200a6966205b202d66202f6d6e742f636f6e' \
                '746578742e7368205d3b207468656e0a20202e202f6d6e742f636f6e7465' \
                '78742e73680a66690a0a686f73746e616d652024484f53544e414d450a69' \
                '66636f6e6669672065746830202449505f50524956415445206e65746d61' \
                '736b20244e45544d41534b200a726f757465206164642064656661756c74' \
                '2067772024474154455741592065746830200a0a6563686f20226e616d65' \
                '7365727665722024444e5322203e202f6574632f7265736f6c762e636f6e' \
                '660a200a2320546f206d616b652073736820776f726b20696e2044656269' \
                '616e204c656e6e793a0a236170742d67657420696e7374616c6c20756465' \
                '760a236563686f20226e6f6e65202f6465762f7074732064657670747320' \
                '64656661756c74732030203022203e3e202f6574632f66737461620a236d' \
                '6f756e74202d610a' + start_script
            context_vars['TARGET'] = 'hdc'
            
            return context_vars
            
    def add_compute_vm(self, app_id, driver, name):
        instance = driver.add_compute_node(cloud_name=self.cloud_name,
                                           instance_name='comp1',
                                           image_id=self.image_id,
                                           size_id=self.size_id,
                                           vnet_id=self.vnet_id,
                                           location_name=self.location_name,
                                           access_id=self.access_id,
                                           secret_key=self.secret_key,
                                           keyname=self.keyname,
                                           security_group=self.security_group,
                                           userdata=self.generate_context(name))

        if app_id in self.private_pool:
            self.private_pool[app_id].append(instance)
        else:
            self.private[app_id] = [instance]
    
    def remove_compute_vm(self, app_id, driver, instance_name):
        if app_id not in self.private_pool:
            #log('No private compute VM for application %s' % app_id)
            return
        
        instances = [instance for instance in self.private_pool[app_id] if instance.name == instance_name]
    
        #if len(instances) == 0:
            #log("Instance does not exist")
    
        self.private_pool[app_id].remove(instances[0])
        driver.remove_compute_node(cloud_name=self.cloud_name,
                                   instance=instances[0],
                                   username=self.access_id,
                                   secret=self.secret_key)
    
    def get_private_pool_size(self, app_id):
        return len(self.private_pool[app_id])

    def add_compute_nodes(self, app_id, no_nodes, driver):
        for i in range(no_nodes):
            self.add_compute_vm(app_id, driver, 'comp1')

    def wait_for_nodes(self, nodes, driver):
        
        while True:
            all_nodes_up = True
            for node in nodes:
                running_hosts = driver.list_compute_hosts()

                if node not in running_hosts:
                    all_nodes_up = False

            if all_nodes_up:
                break

            time.sleep(10) 

    
class BaseClouds:
    def __init__(self):
        self.__available_clouds = []
        self.__active_cloud_index = -1

    def add_cloud(self, base_cloud):
        self.__available_clouds.append(base_cloud)

    def set_active_cloud(self, index):
        self.__active_cloud_index = index

    def get_cloud(self, cloud_name):
        for cloud in self.__available_clouds:
            if cloud.cloud_name == cloud_name:
                return cloud

        return None

    def get_active_cloud(self):
        return self.__available_clouds[self.__active_cloud_index]

    def prepare_migration(self, appid, src_cloud, dst_cloud, driver):
        source_cloud = self.get_active_cloud()

        if source_cloud.cloud_name != src_cloud:
            #log("Cannot migrate from the given cloud")
            return

        destination_cloud = self.get_cloud(dst_cloud)
        
        if destination_cloud == None:
            #log("The destination cloud is not available")
            return

        #no_compute_nodes = source_cloud.get_private_pool_size(appid)
        no_compute_nodes = 1
        destination_cloud.add_compute_nodes(appid, no_compute_nodes, driver)
        destination_cloud.wait_for_nodes(['comp1'], driver)

cloud1 = NestedCloud(cloud_name="EC2", image_id='835',
                           size_id='0', vnet_id='1', location_name="", access_id="aion",
                           secret_key='', keyname="", security_group="")


cloud2 = NestedCloud(cloud_name="OpenNebula", image_id='835',
                           size_id=1, vnet_id=1, location_name="", access_id="aion",
                           secret_key='', keyname="", security_group="")

base_clouds = BaseClouds()

base_clouds.add_cloud(cloud1)
base_clouds.add_cloud(cloud2)

base_clouds.set_active_cloud(0)
