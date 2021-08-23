#!/usr/bin/env python3
"""
Fake Metrics - Fake Prometheus metrics for debugging

Usage:
    fake_metrics static <file>... [-p=<port>] [--host=<host>] [--template=<template> --config=<config>]
    fake_metrics template <file> [-p=<port>] [--host=<host>]
    fake_metrics -h|--help

Commands:

    static                Use a static file from one exporter to constantly
                          export the same statistics.

    template              Use a Jinja template to dynamically adapt the provided
                          metrics.

Options:
    -h --help             Show this screen.
    -p=<port>             The port to listen on [Default: 8888].
    --host=<host>         The host to listen on [Default: 0.0.0.0].
    --template=<template> Configuration Jinja2 template.
    --config=<config>     Output configuration file that will be written.

Default ports:
    Ceph exporter   9283
    Node exporter   9100

Other hints:

Note that `honor_labels` should be set to true to preserve the values of the
mocked metrics in labels like `instance`, which are added by Prometheus when
data is scraped.
"""

import docopt
import socket
import re
import os
from threading import Thread
from urllib.parse import urlparse
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import List, Tuple, Optional
from jinja2 import Template, Environment

from template_tools import increase, increase_or_reset, reset, chance


def port_available(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    r = s.connect_ex(("127.0.0.1", port))
    s.close()
    return r != 0


def createRequestHandler(file: Optional[str] = None, template: Optional[Template] = None):
    assert file or template

    class RequestHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            path = urlparse(self.path)
            if path.path == "/":
                self._index()
            elif path.path == "/metrics":
                self._metrics()

        def _index(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"""
                <html>
                    <head>
                        <meta http-equiv="refresh" content="0; URL='/metrics'" />
                    </head>
                    <body>
                        <p>Redirecting to /metrics!</p>
                    </body>
                </html>""")

        def _metrics(self):
            if file:
                with open(file) as f:
                    content = f.read()
            elif template:
                content = template.render()
            else:
                raise Exception("no content provided to serve")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(content.strip().encode("utf8"))

    return RequestHandler


def run_file(host: str, port: int, file: str):
    print("server started on port {}, serving file {}".format(port, file))
    httpd = HTTPServer((host, port), createRequestHandler(file=file))
    httpd.serve_forever()


def run_template(host: str, port: int, template: Template):
    print("server started on port {}, serving content".format(port))
    httpd = HTTPServer((host, port), createRequestHandler(template=template))
    httpd.serve_forever()


def any_in(search_keys: List[str], haystack: str) -> bool:
    for key in search_keys:
        if key in haystack:
            return True
    return False


def write_config_by_template(
    template_file: str,
    config_file: str,
    starting_port: int,
    files: List[str],
    prometheus_exporter_file_prefix: str = "ceph_mgr_exporter-",
    node_exporter_file_prefix: str = "node_exporter-",
    ignore_suffix: str = ".txt",
):
    """
    Writes a configuration file based on the given files to serve and the
    provided template.

    The provided files are used to determine the necessary configuration for
    Prometheus, so that the resulting Prometheus configuration file is aware of
    any exporters created by this script.
    """
    def clean_str(prefix: str, suffix: str, string: str) -> str:
        string = re.sub(r"^{}".format(prefix), "", string)
        string = re.sub(r"{}$".format(suffix), "", string)
        return string

    files = [os.path.basename(f) for f in files]

    ceph_exporter_hostnames = [
        clean_str(prometheus_exporter_file_prefix, ignore_suffix, f) for f in files
        if f.startswith(prometheus_exporter_file_prefix)
    ]
    node_exporter_hostnames = [
        clean_str(node_exporter_file_prefix, ignore_suffix, f) for f in files
        if f.startswith(node_exporter_file_prefix)
    ]

    port = starting_port

    ceph_exporter_targets: List[Tuple[str, int]] = []
    for hostname in ceph_exporter_hostnames:
        ceph_exporter_targets.append((hostname, port))
        port += 1

    node_exporter_targets: List[Tuple[str, int]] = []
    for hostname in node_exporter_hostnames:
        node_exporter_targets.append((hostname, port))
        port += 1

    with open(template_file, "r") as f:
        config_content = f.read()

    with open(config_file, "w") as f:
        template = Template(config_content)
        f.write(
            template.render(
                ceph_exporter_targets=ceph_exporter_targets,
                node_exporter_targets=node_exporter_targets,
            ))

def serve_static():
    host = args["--host"]
    port = int(args["-p"])
    template = args["--template"]
    config = args["--config"]
    files = args["<file>"]

    def ensure_free_port(port):
        if not port_available(port):
            port += 1
            ensure_free_port(port)
        return port

    port = ensure_free_port(port)  # starting port

    if template and config:
        write_config_by_template(template, config, port, files)

    for file in args["<file>"]:
        t = Thread(target=run_file, args=(host, port, file))
        t.start()
        port += 1

def serve_template():
    host = args["--host"]
    port = int(args["-p"])
    file = args["<file>"][0]

    env = Environment(autoescape=False)  # FIXME unused?
    with open(file, "r") as fh:
        template = Template(fh.read())
        template.environment.globals.update(
            chance=chance,
            increase=increase,
            reset=reset,
            increase_or_reset=increase_or_reset,
        )
    run_template(host, port, template)


if __name__ == "__main__":
    args = docopt.docopt(__doc__)
    if args["static"]:
        serve_static()
    elif args["template"]:
        serve_template()
