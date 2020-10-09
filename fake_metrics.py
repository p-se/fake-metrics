#!/usr/bin/env python3

"""
Fake Metrics - Fake Prometheus metrics for debugging

Usage:
    fake_metrics <file> [-p=<port>] [--host=<host>]
    fake_metrics -h|--help

Options:
    -h --help      Show this screen.
    -p=<port>      The port to listen on [Default: 8888].
    --host=<host>  The host to listen on [Default: 0.0.0.0].

Default ports:
    Ceph exporter   9283
    Node exporter   9100

Other hints:

Note that `honor_labels` should be set to true to preserve
the values of the mocked metrics in labels like `instance`.
"""

import docopt
import cherrypy
import socket

def port_available(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = s.connect_ex(('127.0.0.1', port))
    s.close()
    return r != 0


class Serve:
    def __init__(self, file):
        self.file = file

    @cherrypy.expose
    def index(self):
        return '''
            <html>
                <head>
                    <meta http-equiv="refresh" content="0; URL='/metrics'" />
                </head>
                <body>
                    <p>Redirecting to /metrics!</p>
                </body>
            </html>'''

    @cherrypy.expose
    def metrics(self):
        cherrypy.response.headers['Content-Type'] = 'text/plain; version=0.0.4; charset=utf-8'
        with open(self.file) as f:
            return ''.join(f.readlines())

if __name__ == '__main__':
    args = docopt.docopt(__doc__)
    # print(args)
    host = args['--host']
    port = int(args['-p'])

    def ensure_free_port(port):
        if not port_available(port):
            port += 1
            ensure_free_port(port)
        return port

    port = ensure_free_port(port)

    cherrypy.config.update({
        'server.socket_host': host,
        'server.socket_port': port,
    })
    cherrypy.quickstart(Serve(args['<file>']))
