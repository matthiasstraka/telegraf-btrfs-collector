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
    print(makeLineProtocol(measurement, tagset, values))

def processFilesystem(uuid):
    path = os.path.join(basedir, uuid)

    tagset = {"uuid": uuid}
    tagset["label"] = readFile(os.path.join(path, "label"))

    values = {}

    # read global reserve
    try:
        tagset["profile"] = "single"
        tagset["type"] = "globalreserve"
        profilepath = os.path.join(path, "allocation")
        values = {
            "total_bytes": int(readFile(os.path.join(profilepath, "global_rsv_size")))
        }
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

            values = {
                "bytes_used":  int(readFile(os.path.join(profilepath, "bytes_used"))),
                "total_bytes": int(readFile(os.path.join(profilepath, "total_bytes"))),
                "disk_total":  int(readFile(os.path.join(profilepath, "disk_total"))),
                "disk_used":   int(readFile(os.path.join(profilepath, "disk_used")))
            }
            emitLine(tagset, values)
        except:
            pass

# find all available BTRFS filesystems
for folder in os.listdir(basedir):
    path = os.path.join(basedir, folder)
    if isFilesystem(folder) and os.path.isdir(path):
        processFilesystem(folder)
