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
    print(args)
    cherrypy.config.update({
        'server.socket_host': args['--host'],
        'server.socket_port': int(args['-p']),
    })
    cherrypy.quickstart(Serve(args['<file>']))
