# telegraf-btrfs-collector
Python script that collects BTRFS information for telegraf/InfluxDB

# About
This Python script can be used to collect data about BTRFS from a linux system by reading information from `/sys/fs/btrfs/` without the need for sudo.

## What data is collected
TODO

## Related information
https://godoc.org/github.com/prometheus/procfs/btrfs

# Usage
1. Copy `btrfs-collector.py` to a location accessible by telgraf. For example `/etc/telegraf/btrfs-collector.py`.
2. Update `/etc/telegraf/telegraf.conf` to call the script:

```
    [[inputs.exec]]
    commands = [
        "python3 /etc/telegraf/btrfs-collector.py"
        ]
    timeout = "5s"
    data_format = "influx"
```
3. Restart the telegraf service (e.g. `sudo systemctl restart telegraf.service`)

# Requirements
* python3
* BTRFS filesystem
* telegraf
* InfluxDB
