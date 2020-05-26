# telegraf-btrfs-collector

## About
[Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) is an open-source collector for various metrics.
These metric are usually stored in an [Influx database](https://www.influxdata.com/products/influxdb-overview/).
So far, there is no explicit support for [BTRFS](https://btrfs.wiki.kernel.org/index.php/Main_Page) filesystems, only generic data collected by the `disk` plugin.

This Python script collectss data about BTRFS from a linux system by reading information from `/sys/fs/btrfs/`.
It does not require `root` rights to do so (and can be run directly from the telegraf service).
The output consists of data items in Influx [Line Protocol](https://v2.docs.influxdata.com/v2.0/reference/syntax/line-protocol/) format, which can be directly used to insert the data influx databases.

## What data is collected
Currently, we evaluate only allocation specific data.
This is similar to what can be queries by `btrfs filesystem df /mnt`.
Colleting more non-root-accessible data is planned.
The following data items are collected for each allocation type (data, metadata, system):
* bytes_used
* total_bytes
* disk_total
* disk_used

### Example output
```
btrfs,uuid=25c1fbee-f3ef-4b71-a925-55b8e7667968,label=DATA,profile=single,type=globalreserve total_bytes=536870912i
btrfs,uuid=25c1fbee-f3ef-4b71-a925-55b8e7667968,label=DATA,profile=raid1,type=data bytes_used=721085935616i,total_bytes=795642691584i,disk_total=1591285383168i,disk_used=1442171871232i
btrfs,uuid=25c1fbee-f3ef-4b71-a925-55b8e7667968,label=DATA,profile=raid1,type=metadata bytes_used=1041514496i,total_bytes=2147483648i,disk_total=4294967296i,disk_used=2083028992i
btrfs,uuid=25c1fbee-f3ef-4b71-a925-55b8e7667968,label=DATA,profile=raid1,type=system bytes_used=147456i,total_bytes=67108864i,disk_total=134217728i,disk_used=294912i
```

## Related information
https://godoc.org/github.com/prometheus/procfs/btrfs

## Usage
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

## System Requirements
The following list of requirements basically shows the test-system.
Older versions of the components are likely supported as well.
* Linux (tested with Debian 10)
* Python (tested with version 3.7)
* BTRFS filesystem (tested with version 4.20.1)
* telegraf (tested with version 1.14.3)
* InfluxDB

## Contributing
There are many ways to contribute:
- Fix and report bugs
- Implement more features
- Improve the documentation
- Review the code
