#!/usr/bin/env python
# Copyright (c) 2007 Marc Butler

# Recursively copy a ftp site.

from ftplib import *
import string
import re
import os
import getpass
import sys
import getopt


def listing(ftp):
    entries = []
    ftp.retrlines('LIST', lambda l: entries.append(l))
    
    dpat = re.compile('^d')
    fpat = re.compile('^-')
    totpat = re.compile('^total \d+')
    
    dirs = []
    files = []
    # fixme: does not handle filenames with spaces in them.
    for e in entries:
        if dpat.match(e):
            dirs.append(string.split(e)[-1])
        elif fpat.match(e):
            files.append(string.split(e)[-1])
        else:
            # ignore the total line.
            if not totpat.match(e):
                print 'Warning unhandled dir entry: e=%s' % e

    return dirs, files


def download(ftp, remote, local):
    f = open(local, 'wb')
    ftp.retrbinary('RETR ' + remote, lambda b: f.write(b))
    f.close()

    
def canonize_paths(ftp, names):
    p = ftp.pwd()
    return map(lambda n: p + '/' + n, names)


def copy_site(ftp, exlist):

    all_files = []
    all_dirs = []

    ftp_root = ftp.pwd()
    dir_stack = [ ftp_root ]
    to_local_path = lambda f: '.' + f[len(ftp_root):len(f)]
    
    while dir_stack:
        d = dir_stack.pop()
        ftp.cwd(d)
        print 'Searching %s ...' % d
        
        dirs, files = listing(ftp)
        for d in dirs:
            if d in exlist:                
                i = dirs.index(d)
                del dirs[i]
                print 'Excluded dir: %s' % d                
        dirs = canonize_paths(ftp, dirs)
        map(lambda d: dir_stack.append(d), dirs)
        map(lambda d: all_dirs.append(d), dirs)
        
        files = canonize_paths(ftp, files)
        map(lambda f: all_files.append(f), files)

    # create the local dir tree
    for d in all_dirs:
        ldir = to_local_path(d)
        if not os.path.exists(ldir):
            os.mkdir(ldir)
    
    fcount = len(all_files)
    fnum = 1
    for f in all_files:
        lfile = to_local_path(f)
        print 'Download (%d/%d): %s ...' % (fnum, fcount, f)
        download(ftp, f, lfile)
        fnum += 1

        
def usage():
    print """
ftpcopy.py [options] [site] [user] [password]'

options:
    -x dir : Comma separated list of files to exclude on ftp server.
"""

try:
    optlist, args = getopt.getopt(sys.argv[1:], 'x:h')
    
    if len(args) == 0:
        print usage()
        sys.exit(1)
        
    exlist = []
    for o, a in optlist:
        if o == '-h':
            usage()
            sys.exit(1)
        elif o == '-x':
            if a.find(',') == -1:
                exlist = [ a ]
            else:
                exlist = a.split(',')
        else:
            'Invalid option: %s' % o
            usage()
            sys.exit(1)
    
    print args
    if len(args) > 0:
        site = args[0]
    else:
        site = raw_input('site: ')
    if len(args) > 1:
        user = args[1]
    else:
        user = raw_input('user: ')
    if len(args) > 2:
        passwd = args[2]
    else:
        passwd = getpass.getpass('password: ')

    print 'Site: %s' % site
    print 'User: %s' % user
    
    ftp = FTP(site)
    ftp.login(user, passwd)
    copy_site(ftp, exlist)
    ftp.quit()
    
    print 'Done!'
except Exception, inst:
    print inst
