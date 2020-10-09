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
