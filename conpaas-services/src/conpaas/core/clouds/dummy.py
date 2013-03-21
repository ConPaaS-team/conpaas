'''
Copyright (c) 2010-2012, Contrail consortium.
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
'''

from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

from .base import Cloud


class DummyCloud(Cloud):
    '''Support for "dummy" clouds'''

    def __init__(self, cloud_name, iaas_config):
        Cloud.__init__(self, cloud_name)

    def get_cloud_type(self):
        return 'dummy'

    def _connect(self):
        '''Connect to dummy cloud'''
        DummyDriver = get_driver(Provider.DUMMY)
        self.driver = DummyDriver(0)
        self.connected = True

    def config(self, config_params={}, context=None):
        if context is not None:
            self.cx = context

    def new_instances(self, count, name='conpaas', inst_type=None):
        if not self.connected:
            self._connect()

        return [self._create_service_nodes(self.driver.create_node(), False)
                for _ in range(count)]

    def kill_instance(self, node):
        '''Kill a VM instance.

        @param node: A ServiceNode instance, where node.id is the vm_id
        '''
        if self.connected is False:
            raise Exception('Not connected to cloud')

        # destroy_node does not work properly in libcloud's dummy
        # driver. Just return True.
        return True
