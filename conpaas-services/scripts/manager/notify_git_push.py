#!/usr/bin/env python

import simplejson

from conpaas.core import https


def main():
    https.client.conpaas_init_ssl_ctx('/etc/cpsmanager/certs', 'user')
    method = 'git_push_hook'
    manager_ip = '127.0.0.1'
    res = https.client.jsonrpc_post(manager_ip, 443, '/', method)

    if res[0] == 200:
        try:
            data = simplejson.loads(res[1])
        except simplejson.decoder.JSONDecodeError:
            # Not JSON, simply return what we got
            return res[1]

        return data.get('result', data)

    raise Exception("Call to method %s on %s failed with HTTP code %s: %s."
                    % (method, manager_ip, res[0], res[1]))


if __name__ == "__main__":
    res = main()
    print "%s" % res
