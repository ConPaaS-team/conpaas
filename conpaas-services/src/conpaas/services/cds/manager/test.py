#!/usr/bin/python

import json
import sys

from manager import ContentDeliveryManager


def unpack_params(args):
    if len(args) == 1:
        raise Exception('method not specified')
    method = args[1]
    params = {}
    for i in xrange(2, len(args)):
        try:
            (key, value) = args[i].split('=')
            params[key] = value
        except:
            continue
    return (method, params)

def run_tests():
    pass

def main():
    cds = ContentDeliveryManager(True)
    (method, params) = unpack_params(sys.argv)
    try:
        function = getattr(cds, method)
    except AttributeError:
        print 'Method "%s" does not exist' %(method)
        exit()
    # do the call
    response = function(params)
    try:
        print json.dumps(response.obj)
    except AttributeError:
        print response.message

if __name__ == '__main__':
    main()
