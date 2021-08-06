#!/bin/python3

import os
import re

###############################################################################
# Configuration
###############################################################################
# Base-dir for BTRFS information
basedir = "/sys/fs/btrfs/"
measurement = "btrfs"

def isFilesystem(folder):
    return re.fullmatch("[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}", folder) is not None

def readFile(path):
    ''' Read a single line file '''
    with open(path, "r") as f:
        return f.read().rstrip('\n')

def makeLineProtocol(measurement, tags, values):
    ''' Convert to influx line protocol data line: measurement,tag1=name1,tag2=name2 field1=value1,field2=value2 ''' 
    measurementid = measurement + ","
    measurementid += ",".join(["{}={}".format(k, v) for k,v in tags.items()])
    valuelist =      ",".join(["{}={}i".format(k, v) for k,v in values.items()])
    return measurementid + " " + valuelist

def emitLine(tagset, values):
    if len(values) == 0:
        return
    print(makeLineProtocol(measurement, tagset, values))

def readExistingValues(fileset, path):
    result = {}
    for name, filename in fileset.items():
        try:
            result[name] = int(readFile(os.path.join(path, filename)))
        except:
            pass
    return result

def processFilesystem(uuid):
    path = os.path.join(basedir, uuid)

    tagset = {"uuid": uuid}
    tagset["label"] = readFile(os.path.join(path, "label"))

    # read global attributes
    files = {
        'generation': 'generation'
    }
    values = readExistingValues(files, path)
    emitLine(tagset, values)

    # read global reserve
    try:
        tagset["profile"] = "single"
        tagset["type"] = "globalreserve"
        profilepath = os.path.join(path, "allocation")
        global_files = { 'total_bytes': 'global_rsv_size' }
        values = readExistingValues(global_files, profilepath)
        emitLine(tagset, values)
    except:
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
            values = readExistingValues(allocation_files, profilepath)

            emitLine(tagset, values)
        except:
            pass

# find all available BTRFS filesystems
for folder in os.listdir(basedir):
    path = os.path.join(basedir, folder)
    if isFilesystem(folder) and os.path.isdir(path):
        processFilesystem(folder)
