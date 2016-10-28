#!/usr/bin/env python
from pathlib import Path, PurePath
import json
import re
import urllib.request
import urllib.error
import sys

WEB_PATH = '/data0/web/'

def discover(path):
    ports = [ {'{#WEBDOMAIN}':PurePath(p).name} for p in Path(path).glob('*') if p.is_dir() and re.match('.*\..*', PurePath(p).name) ]
    print(json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':')))

def status(domain):
    url = 'http://{0}'.format(domain)
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req) as r:
            print(r.getcode())
    except urllib.error.URLError as e:
        print(e.code) if hasattr(e, 'code') else print(555)
        #with open('web.log','a') as logfile:
        #    logfile.write(str(e))

if __name__ == '__main__':
    discover(WEB_PATH) if len(sys.argv) == 1 else status(sys.argv[1])
	
