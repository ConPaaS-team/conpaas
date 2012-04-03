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

Created on Jan 25, 2012

@author: aaasz
@file
'''

''' Cloud interface '''
class Cloud:

    def __init__(self, cloud_name):
        self.cloud_name = cloud_name

    def get_cloud_name(self):
        return self.cloud_name

    def get_cloud_type(self):
        raise NotImplementedError, \
             'get_cloud_type not implemented for this cloud driver'

    def get_context_template(self):
        raise NotImplementedError, \
             'get_context not implemented for this cloud driver'

    def set_context_template(self, cx):
        raise NotImplementedError, \
             'set_context not implemented for this cloud driver'

    def config(self, config_params, context):
        raise NotImplementedError, \
             'config not implemented for this cloud driver'

    def list_vms(self):
        raise NotImplementedError, \
             'list_vms not implemented for this cloud driver'

    def new_instances(self, count):
        raise NotImplementedError, \
             'new_instances not implemented for this cloud driver'

    def kill_instance(self, vm_id):
        raise NotImplementedError, \
             'kill_instance not implemented for this cloud driver'


