"""
Copyright (c) 2010-2013, Contrail consortium.
All rights reserved.

Redistribution and use in source and binary forms, 
with or without modification, are permitted provided
that the following conditions are met:

 1. Redistributions of source code must retain the
    above copyright notice, this list of conditions
    and the following disclaimer.
 2. Redistributions in binary form must reproduce
    the above copyright notice, this list of 
    conditions and the following disclaimer in the
    documentation and/or other materials provided
    with the distribution.
 3. Neither the name of the Contrail consortium nor the
    names of its contributors may be used to endorse
    or promote products derived from this software 
    without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, 
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR 
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS 
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
"""
import subprocess

from subprocess import Popen
from os.path import join

from Cheetah.Template import Template


from conpaas.core.expose import expose
from conpaas.core.https.server import HttpJsonResponse, HttpErrorResponse
from conpaas.core.agent import BaseAgent

class HadoopNaasAgent(BaseAgent):
    """Agent class with the following exposed methods:

    check_agent_process() -- GET
    create_hub(my_ip) -- POST
    create_node(my_ip, hub_ip) -- POST
    """
    ETC = '/opt/hadoopnaas/hadoop-1.0.4-custom/conf/'

    def __init__(self, config_parser, **kwargs): 
        """Initialize BluePrint Agent.
  
        'config_parser' represents the agent config file.
        **kwargs holds anything that can't be sent in config_parser.
        """
        BaseAgent.__init__(self, config_parser)


    @expose('POST')
    def create_node(self, kwargs):
        self.logger.info('Node starting up')

        self.state = 'ADAPTING'

        self.my_ip_address = kwargs['my_ip']
        #Do something on agent startup

        self.state = 'RUNNING'
        self.logger.info('Node started up')
        return HttpJsonResponse()

    @expose('GET')
    def test(self, kwargs):
        self.logger.info('Test method started')

        self.state = 'ADAPTING'

        msg = "hello kitty"
        
        self.state = 'RUNNING'
        self.logger.info('Test method ended')
        return HttpJsonResponse({'msg': msg})

    @expose('GET')
    def start_all(self, kwargs):
        subprocess.call('export HADOOP_SSH_OPTS="-o StrictHostKeyChecking=no" ; /opt/hadoopnaas/hadoop-1.0.4-custom/bin/start-all.sh', shell=True)
        return HttpJsonResponse({'msg': 'done'})


    @expose('GET')
    def make_worker(self, kwargs):
        subprocess.call("cd /opt/hadoopnaas/; rm -rf hadoop-1.0.4-custom/",shell=True)
        subprocess.call("cd /opt/hadoopnaas/; cp -rf hadoop-1.0.4-custom-worker/ hadoop-1.0.4-custom/",shell=True)
        return HttpJsonResponse({'msg': 'done'})

    @expose('POST')
    def setup_node(self,kwargs):

        self.logger.debug('called _setup_node')

        try:

            # ip = kwargs['nodeip']
            # with open("/etc/hosts", "a") as myfile:
            #     myfile.write('\n'+str(ip)+' conpaas'+'\n')

            tmpl = open(join(self.ETC, 'core-site.xml.tmpl')).read()
            cnfg = open(join(self.ETC, 'core-site.xml'), 'w')
            template = Template(tmpl, { 'HDFS_MASTER' : kwargs['master']['ID'] })
            cnfg.write(str(template))
            cnfg.close()

            tmpl = open(join(self.ETC, 'shim.properties.tmpl')).read()
            cnfg = open(join(self.ETC, 'shim.properties'), 'w')
            template = Template(tmpl, { 'NAASBOX' : kwargs['naasbox']['ID'] })
            cnfg.write(str(template).replace('DefaultDecisionMaker', 'NoShimDecisionMaker'))
            # cnfg.write(str(template))
            cnfg.close()

            # subprocess.call("ssh-keygen -f /root/.ssh/id_rsa -t rsa -N '' ",shell=True)

            if kwargs['ismaster']:

                tmpl = open(join(self.ETC, 'masters.tmpl')).read()
                cnfg = open(join(self.ETC, 'masters'), 'w')
                template = Template(tmpl, { 'MASTER' : kwargs['master']['ID'] })
                cnfg.write(str(template))
                cnfg.close()

                tmpl = open(join(self.ETC, 'mapred-site.xml.tmpl')).read()
                cnfg = open(join(self.ETC, 'mapred-site.xml'), 'w')
                template = Template(tmpl, { 'JOB_TRACKER' : kwargs['master']['ID'] })
                cnfg.write(str(template))
                cnfg.close()

                subprocess.call('echo "Y" | /opt/hadoopnaas/hadoop-1.0.4-custom/bin/hadoop namenode -format',shell=True)
                subprocess.call('mknod -m 666 /dev/tty c 5 0',shell=True)
                subprocess.call("ssh-keygen -f /root/.ssh/id_rsa -t rsa -N '' ",shell=True)

                open('/opt/hadoopnaas/hadoop-1.0.4-custom/conf/slaves','w').close()

            else:

                with open(join(self.ETC, 'masters'),'w') as myfile:
                    myfile.write(kwargs['master']['ID']+"\n")
                    # myfile.write("conpaas\n")

                with open(join(self.ETC, 'slaves'),'w') as myfile:
                    myfile.write(kwargs['node']['ID']+"\n")
                    # myfile.write("conpaas\n")

                tmpl = open(join(self.ETC, 'mapred-site.xml.tmpl')).read()
                cnfg = open(join(self.ETC, 'mapred-site.xml'), 'w')

                if kwargs['isreducer'] == True:
                    template = Template(tmpl, { 'JOB_TRACKER' : kwargs['master']['ID'], 'MAX_REDUCE': '1', 'MAX_MAP': '0' })
                else:
                    template = Template(tmpl, { 'JOB_TRACKER' : kwargs['master']['ID'], 'MAX_REDUCE': '0', 'MAX_MAP': '1' })
                    # template = Template(tmpl, { 'JOB_TRACKER' : kwargs['master']['Address'], 'MAX_REDUCE': '0', 'MAX_MAP': '2' })

                cnfg.write(str(template))
                cnfg.close()

        except Exception as e:

            self.logger.debug('Exception in setup_node: %s', e)

        finally:

            self.logger.info('Hadoop configuration written.')

        return HttpJsonResponse({'msg': 'done'})


    @expose('POST')
    def setup_naasbox(self,kwargs):

        self.logger.debug('called _setup_node')
        
        try:

            # with open("/etc/hosts", "a") as myfile:
            #     myfile.write('\n'+str(kwargs['naasboxip'])+' conpaas'+'\n')

            etc = '/opt/hadoopnaas/hadoopnaasbox/'
            tmpl = open(join(etc, 'naasbox.properties.tmpl')).read()
            cnfg = open(join(etc, 'naasbox.properties'), 'w')
            template = Template(tmpl, { 'NAASBOX' : kwargs['naasbox']['ID'] })
            cnfg.write(str(template))
            cnfg.close()

        except Exception as e:

            self.logger.debug('Exception in setup_naasbox: %s', e)

        finally:

            self.logger.info('Naasbox configuration written.')

        return HttpJsonResponse({'msg': 'done'})

    @expose('POST')
    def enable_ssh(self,kwargs):
        ip = kwargs['node']['Address']
        self.logger.info('enable_ssh %s' % ip)
        for i in range(0,2):
        # for i in range(0,):
            subprocess.call('/opt/hadoopnaas/scripts/enable_remote_ssh.sh '+str(ip),shell=True)
        return HttpJsonResponse({'msg':'done'})

    @expose('POST')
    def append_slaves(self,kwargs):
        nodes = kwargs['nodes']
        for node in nodes:
            hostname = node['ID']
            with open("/opt/hadoopnaas/hadoop-1.0.4-custom/conf/slaves", "a") as myfile:
                myfile.write(str(hostname)+'\n')
        return  HttpJsonResponse({'msg':'done'})

    @expose('POST')
    def fix_hosts(self,kwargs):
        ip = kwargs['ip']
        with open("/etc/hosts", "a") as myfile:
            myfile.write('\n'+str(ip)+' conpaas'+'\n')
        return  HttpJsonResponse({'msg':'done'})

    @expose('POST')
    def update_host(self, kwargs):
        self.logger.info('Update agent hosts')

        self.state = 'ADAPTING'
        me = kwargs.pop('me')
        nodes = kwargs.pop('nodes')
        my_host = me['ID']
        # hosts = '127.0.0.1\tlocalhost\n'
        # hosts = '127.0.0.1\t%s\n' % my_host
        hosts = ''
        for node in nodes:
            # if my_host != node['ID']:
            hosts = hosts + '%s\t%s\n' % (node['Address'], node['ID'])
        self.logger.info('hosts %s' % hosts)
        proc = Popen('hostname %s ; echo %s > /etc/hostname; echo "%s" > /etc/hosts' % (my_host, my_host, hosts), shell=True , close_fds=True)
        proc.wait()

        self.state = 'RUNNING'
        self.logger.info('Hosts updated')
        return HttpJsonResponse()
