#!/usr/bin/env python
#
# Copyright (c) 2011 - Marc Butler
# All Rights Reserved. No warranty.
#
# Interactive tool for identifying and inspecting, and pruning duplicate
# files down to a single copy.
#
# e.g. Find all the files named: rcopy.py
#
# [Backup]$ python rmdup.py rcopy.py
# ------------------------------------------------------------
# 8ac93566c08143ac127b31b574af92b3533ae979 /Users/marc/Documents/Backup/Sony/src/rcopy.py
# 8eb7bb2aae3838b408a7c05381da1cb09f74189c /Users/marc/Documents/Backup/Sony/src/PythonTools/rcopy.py
# 5c89373e3c0d66cd14e3b6ae808d76e1628e2fca /Users/marc/Documents/Backup/Sony/src/pytools/rcopy.py
# ------------------------------------------------------------
# > 
#

from collections import defaultdict
import os
import sys
import re
import hashlib

def usage():
    print """
rmdup.py filename
 
Find duplicate files named filename. Then allow interactive comparison
and handling of each distinct version.
"""
def sha1file(path):
    h = hashlib.sha1()
    f = file(path, "rb")
    h.update(f.read())
    f.close()
    return h.hexdigest()

def find_duplicates(top, filename):
    dups = []
    for root, dirs, files in os.walk(top):
        for name in files:
            if name == filename:
                dups.append(os.path.join(root, name))
    return dups 

def unique_sha1(sha1map, sha1part):
    sha1 = None
    for k in sha1map.keys():
        if sha1part == k[:len(sha1part)]:
            if sha1 == None:
               sha1 = k
            else:
                print 'Error sha1 portion', sha1part, 'is ambiguous'
                return None
    return sha1

def help():
                    print """
    Help:
     q           : quit
     h           : help
     d sha1 sha1 : diff duplicates
     r sha1      : delete all files with that sha1
     v sha1      : view the contents of a file with sha1
     o sha1      : leave only one file with the specified sha1
"""
def single_arg(sha1map, cmd):
    m = re.match('^\s*(.)\s+([\da-f]+)\s*$', cmd)
    if not m: return None, None
    fullsha = unique_sha1(sha1map, m.group(2))
    return m.group(1), fullsha

def interact(sha1map):
    while 1:
        print '-' * 60
        for k in sha1map.keys():
            print k, sha1map[k][0]
        print '-' * 60
        
        cmd = raw_input("> ")
        
        m = re.match('^\s*.\s*$', cmd)
        if m:
            cmd = m.group(0)
            if cmd == 'q':
                break
            elif cmd == 'h' or cmd == '?':
                help()
                continue
            else:
                print 'Unknown command:', cmd
                help()
                continue
                
        cmdlet, fullsha1 = single_arg(sha1map, cmd)
        if cmdlet:
            if not fullsha1: continue
            if cmdlet == 'r':
                for path in sha1map[fullsha1]:
                    print 'Removing...', path
                    os.remove(path)
                del sha1map[fullsha1]
                continue
            elif cmdlet == 'v':                
                os.system('less %s' % sha1map[fullsha1][0])
                continue
            elif cmdlet == 'o':
                lst = sha1map[fullsha1]
                while len(lst) > 1:
                    path = lst.pop()
                    print 'Removing...', path
                    os.remove(path)
                continue                                        
        
        m = re.match('^\s*d\s+([\da-f]+)\s+([\da-f]+)\s*$', cmd)
        if m:
            a = unique_sha1(sha1map, m.group(1))
            b = unique_sha1(sha1map, m.group(2))
            if a and b:
                a = sha1map[a][0]
                b = sha1map[b][0]
                os.system('diff -u %s %s' % (a, b))
            continue
            
        print 'ERROR: Invalid or unrecognized command:', cmd
        help()

def main(args=None):
    if not args: args = sys.argv[1:]
    if len(args) != 1:
        usage()
    
    matches = find_duplicates(os.getcwd(), args[0])
    if len(matches) < 0:
        print 'No duplicates: only found', len(matches), 'files.'
        return 0
    matches = [(sha1file(path), path) for path in matches]
    sha1map = defaultdict(list)
    for k, v in matches: sha1map[k].append(v)
    
    interact(sha1map)
    return 0
    
if __name__ == '__main__':
    sys.exit(main())
