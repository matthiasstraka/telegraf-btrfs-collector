#!/bin/python3
'''
Transforms BTRFS filesystem information to InfluxDB linestrings for use in telegraf
'''

import os
from re import fullmatch

###############################################################################
# Configuration
###############################################################################
# Base-dir for BTRFS information
BASEDIR = "/sys/fs/btrfs/"
MEASUREMENT = "btrfs"

def is_filesystem(folder_name):
    ''' Checks if the folder is a BTRFS filesystem folder '''
    return fullmatch(
        "[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}",
        folder_name) is not None

def read_file(path_name):
    ''' Read a single line file '''
    with open(path_name, "r") as handle:
        return handle.read().rstrip('\n')

def make_line_protocol(measurement, tags, values):
    '''
    Convert to influx line protocol data line:
    measurement,tag1=name1,tag2=name2 field1=value1,field2=value2
    '''
    measurementid = measurement + "," + ",".join([f"{k}={v}" for k, v in tags.items()])
    valuelist = ",".join([f"{k}={v}i" for k, v in values.items()])
    return f"{measurementid} {valuelist}"

def emit_line(tagset, values):
    ''' Prints a single influx line protocol line to the console '''
    if len(values) == 0:
        return
    print(make_line_protocol(MEASUREMENT, tagset, values))

def read_existing_values(fileset, path_name):
    ''' Reads a set of files in path_name '''
    result = {}
    for name, filename in fileset.items():
        try:
            result[name] = int(read_file(os.path.join(path_name, filename)))
        except Exception: # pylint: disable=broad-except
            pass
    return result

def process_filesystem(uuid):
    ''' Process a single filesytem node '''
    path_name = os.path.join(BASEDIR, uuid)

    tagset = {"uuid": uuid}
    tagset["label"] = read_file(os.path.join(path_name, "label"))

    # read global attributes
    files = {
        'generation': 'generation'
    }
    values = read_existing_values(files, path)
    emit_line(tagset, values)

    # read global reserve
    try:
        tagset["profile"] = "single"
        tagset["type"] = "globalreserve"
        profilepath = os.path.join(path, "allocation")
        global_files = {'total_bytes': 'global_rsv_size'}
        values = read_existing_values(global_files, profilepath)
        emit_line(tagset, values)
    except Exception: # pylint: disable=broad-except
        pass

    # read allocation data
    for atype in ['data', 'metadata', 'system']:
        try:
            tagset["type"] = atype
            profilepath = os.path.join(path, "allocation", atype)

            #detect data profile (there is a subfolder named after the profile)
            del tagset["profile"]
            for profile in ['single', 'dup', 'raid0', 'raid1', 'raid10', 'raid5', 'raid6']:
                if os.path.isdir(os.path.join(profilepath, profile)):
                    tagset["profile"] = profile

            allocation_files = {
                "bytes_used":     "bytes_used",
                "bytes_readonly": "bytes_readonly",
                "total_bytes":    "total_bytes",
                "disk_total":     "disk_total",
                "disk_used":      "disk_used",
            }
            values = read_existing_values(allocation_files, profilepath)

            emit_line(tagset, values)
        except Exception: # pylint: disable=broad-except
            pass

# find all available BTRFS filesystems
for folder in os.listdir(BASEDIR):
    path = os.path.join(BASEDIR, folder)
    if is_filesystem(folder) and os.path.isdir(path):
        process_filesystem(folder)
