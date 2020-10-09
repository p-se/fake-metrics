# Fake metrics for Prometheus

Serves snapshots of Prometheus exporters for debugging purposes.

## Usage Examples

### Single Snapshot

```bash
./fake_metrics.py <file>
```

### Multiple Snapshots

Fake metrics can open multiple ports to serve data. If more than one file is
passed to it, it will take the default port and increase it by one for each
consecutive file.

```bash
./fake_metrics.py data/*
```

The server tells you which ports are being used for which provided files.

```bash
$ ./fake_metrics.py data/*
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
