#!/usr/bin/env python3

"""
Fake Metrics - Fake Prometheus metrics for debugging

Usage:
    fake_metrics <file>... [-p=<port>] [--host=<host>]
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
import socket
from threading import Thread
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler

def port_available(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = s.connect_ex(('127.0.0.1', port))
    s.close()
    return r != 0


def createRequestHandler(file):
    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path)
            if path.path == '/':
                self._index()
            elif path.path == '/metrics':
                self._metrics()

        def _index(self):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''
                <html>
                    <head>
                        <meta http-equiv="refresh" content="0; URL='/metrics'" />
                    </head>
                    <body>
                        <p>Redirecting to /metrics!</p>
                    </body>
                </html>''')

        def _metrics(self):
            with open(file) as f:
                content = ''.join(f.readlines())
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(content.strip().encode('utf8'))

    return RequestHandler



def run(host, port, file):
    print('server started on port {}, serving file {}'.format(port, file))
    httpd = HTTPServer((host, port), createRequestHandler(file))
    httpd.serve_forever()


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

    for file in args['<file>']:
        t = Thread(target=run, args=(host, port, file))
        t.start()
        port += 1


