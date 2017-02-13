#!/usr/bin/env python
from pathlib import Path, PurePath
import json
import re
import urllib.request
import urllib.error
import sys
import logging

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/data0/logs/zabbix_agent/web_monitor.log',
                filemode='a')

WEB_PATH = '/data0/web/'

def discover(path):
    ports = [ {'{#WEBDOMAIN}':p.name} for p in Path(path).glob('*') if p.is_dir() and re.match('.*\..*', p.name) ]
    print(json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':')))

def status(domain):
    url = 'http://{0}'.format(domain)
    req = urllib.request.Request(url, method='HEAD')
    try:
        with urllib.request.urlopen(req) as r:
            print(r.getcode())
    except urllib.error.URLError as e:
        print(555)
        mes = '"{0}" DOMAIN {1}'.format(e, domain)
        logging.error(mes)

if __name__ == '__main__':
    discover(WEB_PATH) if len(sys.argv) == 1 else status(sys.argv[1])
	
