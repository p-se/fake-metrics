# Fake metrics for Prometheus

Serves snapshots of Prometheus exporters for debugging purposes.

It can also create Prometheus configuration files with an appropriate template.

## Usage

Please issue `./fake_metrics -h` to see the full usage.

## Usage Notes

Note that every request to the fake metrics server may increase a counter. By
requesting the data from a browser while Prometheus is scraping them
simultaneously, you may cause unwanted changes in your metrics.

On the other hand, you can deliberately exploit this fact if you want to
cause an ad hoc change in the metrics. When time passes by, the metrics
should return to the configured behavior.

## Usage Examples

### Single Snapshot

```bash
./fake_metrics.py static <txt_file>
./fake_metrics.py template <jinja_file>
```

### Multiple Snapshots

Fake metrics can open multiple ports to serve data. If more than one file is
passed to it, it will take the default port and increase it by one for each
consecutive file. Currently multiple snapshots only support static files.

```bash
./fake_metrics.py static data/*
```

The server tells you which ports are being used for which provided files.

```bash
$ ./fake_metrics.py static data/*
server started on port 8888, serving file data/ceph_mgr_exporter-ses6-mon1.txt
server started on port 8889, serving file data/ceph_mgr_exporter-ses6-mon2.txt
server started on port 8890, serving file data/ceph_mgr_exporter-ses6-mon3.txt
server started on port 8891, serving file data/node_exporter-ses6-mon1.txt
server started on port 8892, serving file data/node_exporter-ses6-mon2.txt
server started on port 8893, serving file data/node_exporter-ses6-mon3.txt
server started on port 8894, serving file data/node_exporter-ses6-osd01.txt
server started on port 8895, serving file data/node_exporter-ses6-osd02.txt
server started on port 8896, serving file data/node_exporter-ses6-osd03.txt
server started on port 8897, serving file data/node_exporter-ses6-osd04.txt
```

## Prometheus Configuration

Fake metrics can create a complete or partial Prometheus configuration file. To do so, a Jinja2
template must be specified.

```jinja2
scrape_configs:
  - job_name: prometheus
    static_configs:
      - targets: ["localhost:9090"]

  - job_name: ceph-fake-metrics
    honor_labels: true
    static_configs:
      - targets:
      {%- for hostname, port in ceph_exporter_targets %}
          - "localhost:{{port}}"
      {%- endfor %}

  {% for hostname, port in node_exporter_targets %}
  - job_name: {{hostname}}
    static_configs:
      - targets:
          - "localhost:{{port}}"
    relabel_configs:
      - source_labels: ["job"]
        target_label: instance
        replacement: "$1"
  {% endfor %}
alerting:
  alertmanagers:
    - scheme: http
      static_configs:
        - targets:
            - alertmanager:9093
            - localhost:9093
```

## Future

- Separate configuration file creation from serving fake metrics.
- The prefix and suffix of filenames that should be discarded to get to the
  hostname need to be customizable.
- Maybe enable to start a docker container in network mode host with the created
  configuration file?

## Alternatives

Alternatively, the Node-Exporter could be used to server a text file using the
`textfiles` collector. It is even possible to disable all other data exporter
by the Node-Exporter by default using the `--collector.disable-defaults`
switch. The data exporter would not need to be static if the file(s) is/are
updated.

```sh
prometheus-node-exporter \
    --collector.disable-defaults \
    --collector.textfile  \
    --collector.textfile.directory=/exports
```

Note: All `*.prom` files in the specified directory will be parsed, no more.
