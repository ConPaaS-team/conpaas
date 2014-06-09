from cpsdirector.common import log
import time

nested_cloud = NestedCloud(cloud_name="OpenNebula", image_id='764',
                           size_id='1', vnet_id='1', username='aion',
                           secret='')                           
class NestedCloud():

    def __init__(self, **kwargs):
        self.cloud_name = kwargs['cloud_name']
        self.image_id = kwargs['image_id']
        self.size_id = kwargs['size_id']
        self.vnet_id = kwargs['vnet_id']
        self.username = kwargs['username']
        self.secret = kwargs['secret']
        
        shared_pool = {}
        private_pool = {}
        node_index = 0
        
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
        
        if max_cpu - used_cpu >= 2*cpu_per_node and
            max_ram - used_ram >= 2*ram_per_node:
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
                log("No private resources available")
                return
        
            for instance in self.private_pool[app_id]:
                host = driver.list_compute_hosts[instance.name]
                if self._test_host(host, size):
                    designated_host = instance.name
                    break
            
            if not designated_host:
                log("No private compute VM available to deploy container")
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
            log("no more compute resources available")
            #driver.add_compute_node("node%d" % node_index)
            #node_index += 1   
            
        return None

    def add_compute_vm(self, app_id, driver, name):
        instance = driver.app_compute_node(cloud_name=self.cloud_name,
                                           instance_name=name,
                                           image_id=self.image_id,
                                           size_id=self.size_id,
                                           vnet_id=self.vnet_id,
                                           username=self.username,
                                           secret=self.secret)

        if app_id in self.private_pool:
            self.private_pool[app_id].append(instance)
        else:
            self.private[app_id] = [instance]
    
    def remove_compute_vm(self, app_id, driver, instance_name):
        if app_id no int self.priavte_pool:
            log('No private compute VM for application %s' % app_id)
            return
        
        instances = [instance for instance in self.private_pool[app_id] if instance.name == instance_name]
    
        if len(instances) == 0:
            log("Instance does not exist")
    
        self.private_pool[app_id].remove(instances[0])
        driver.remove_compute_node(cloud_name=self.cloud_name,
                                   instance=instances[0],
                                   username=self.username,
                                   secret=self.secret)
        

