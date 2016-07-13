#!/usr/bin/env python
from pathlib import Path,PurePath
import json

MYSQL_PATH = '/data0/mysql/'

def discover(path):
	ports = [ {'{#REDISPORT}':PurePath(d).name} for d in Path(path).glob('*') if d.is_dir() and PurePath(d).name not in ('3306', '99999') ]
	print(json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':')))
	

discover(MYSQL_PATH)
