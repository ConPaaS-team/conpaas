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

@package conpaas.core
@file
'''


class ServiceNode(object):
    '''
        This class represents the abstraction of a node. A basic node is
        represented by a vmid and an ip address. This class can be extented
        with more information about the node, specific to each service.

    '''

    def __init__(self, vmid, ip, private_ip, cloud_name):
        self.id = vmid
        self.ip = ip
        self.private_ip = private_ip
        self.cloud_name = cloud_name

    def __repr__(self):
        return 'ServiceNode(id=%s, ip=%s)' % (str(self.id), self.ip)

    def __cmp__(self, other):
        if self.id == other.id and self.cloud_name == other.cloud_name:
            return 0
        elif self.id < other.id:
            return -1
        else:
            return 1

    def as_libcloud_node(self):
        class Node:
            pass
        n = Node()
        n.id = self.id
        n.ip = self.ip
        return n
