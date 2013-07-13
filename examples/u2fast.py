#! /usr/bin/env python
#
# Copyright (c) 2013 Jason Ish
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# u2fast.py
#
# This example program reads events from unified2 log files and prints
# them in the "fast" style.

from __future__ import print_function

import sys
import os
import getopt
import socket
import time

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(sys.argv[0]))))

from idstools import unified2
from idstools import maps

proto_map = {
    1: "ICMP",
    6: "TCP",
    17: "UDP",
}

def print_ip(addr):
    if len(addr) == 4:
        return socket.inet_ntoa(addr)
    else:
        parts = struct.unpack("H" * (len(addr) / 2), addr)
        return ":".join("%x" % p for p in parts)

def print_time(sec, usec):
    tt = time.localtime(sec)
    return "%04d/%02d/%02d-%02d:%02d:%02d.%06d" % (
        tt.tm_year, tt.tm_mon, tt.tm_mday, tt.tm_hour, tt.tm_min, tt.tm_sec, 
        usec)

def print_event(event, msgmap, classmap):
    msg_entry = msgmap.get(event["generator-id"], event["signature-id"])
    if msg_entry:
        msg = msg_entry.msg
    else:
        msg = "Snort Event"

    class_entry = classmap.get_by_id(event["classification-id"])
    if class_entry:
        class_description = class_entry.description
    else:
        class_description = str(event["classification-id"])

    proto = proto_map.get(event["protocol"], str(event["protocol"]))

    print("%s [**] [%d:%d:%d] %s [**] [Classification: %s] [Priority: %d] {%s} %s:%d -> %s:%d" % (
            print_time(event["event-second"], event["event-microsecond"]),
            event["generator-id"],
            event["signature-id"],
            event["signature-revision"],
            msg,
            class_description,
            event["priority"],
            proto,
            print_ip(event["ip-source"]),
            event["sport-itype"],
            print_ip(event["ip-destination"]),
            event["dport-icode"],
            ))

def usage(fileobj=sys.stderr):
    print("usage: %s [options] <files...>" % sys.argv[0], file=fileobj)
    print("")
    print("options:")
    print("\t-C <classification.config>", file=fileobj)
    print("\t-G <gen-msg.map>", file=fileobj)
    print("\t-S <sid-msg.map>", file=fileobj)

def main():

    msgmap = maps.MsgMap()
    classmap = maps.ClassificationMap()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hC:G:S:")
    except getopt.GetoptError as err:
        print("error: %s\n" % err, file=sys.stderr)
        usage()
        return 1
    for o, a in opts:
        if o == "-C":
            classmap.load_classification_file(a)
        elif o == "-G":
            msgmap.load_genmsg_file(a)
        elif o == "-S":
            msgmap.load_sidmsg_file(a)
        elif o == "-h":
            usage(sys.stdout)
            return 0

    if not args:
        usage()
        return 1

    reader = unified2.FileEventReader(args)
    for event in reader:
        print_event(event, msgmap, classmap)

if __name__ == "__main__":
    sys.exit(main())
