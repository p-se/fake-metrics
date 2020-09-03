#!/usr/bin/env python3

"""
Fake Metrics - Fake Prometheus metrics for debugging

Usage:
    fake_metrics <file> [-p=<port>]
    fake_metrics -h|--help

Options:
    -h --help   Show this screen.
    -p=<port>   The port to listen on [Default: 8888].
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
        'server.socket_port': int(args['-p'])
    })
    cherrypy.quickstart(Serve(args['<file>']))
