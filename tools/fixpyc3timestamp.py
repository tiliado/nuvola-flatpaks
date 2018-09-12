#!/usr/bin/env python3

import binascii
import os
import sys
import re

TIMESTAMP_RE = re.compile(rb'\d\d?-\w{3}')

OSTREE_TIMESTAMP = bytes(4)
for root, dirs, files in os.walk(sys.argv[1]):
    for filename in files:
        path = os.path.join(root, filename)
        try:
            if filename.endswith(('.opt-1.pyc', '.opt-2.pyc')):
                with open(path, 'r+b') as f:
                    magic = f.read(4)
                    timestamp = f.read(4)
                    if timestamp != OSTREE_TIMESTAMP:
                        #~ print("%s %s %s" % (filename, binascii.hexlify(magic), binascii.hexlify(timestamp)))
                        f.seek(0)
                        magic = f.read(4)
                        f.write(OSTREE_TIMESTAMP)
                        f.seek(4)
                        timestamp = f.read(4)
                        #~ print("%s %s %s" % (filename, binascii.hexlify(magic), binascii.hexlify(timestamp)))
                        print("Fixed timestamp:", path)
            elif filename.endswith('.egg'):
                path = os.path.join(root, filename)
                with open(path, "rb") as f:
                    data = f.read()
                data = TIMESTAMP_RE.sub(b'70-Jan-01 00:00', data)
                with open(path, "wb") as f:
                    f.write(data)
                print("Fixed timestamp:", path)
        except OSError as e:
            if e.errno == 30:
                print('Cannot fix, read-only:', path)
            else:
                raise
    
