#!/usr/bin/env python
from pathlib import Path, PurePath
import json
import re

MYSQL_PATH = '/data0/mysql/'

def discover(path):
	ports = [ {'{#REDISPORT}':PurePath(p).name} for p in Path(path).glob('*') if p.is_dir() and re.match('[1-65535]', PurePath(p).name) ]
	print(json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':')))
	

discover(MYSQL_PATH)
