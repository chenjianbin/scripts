#!/usr/bin/env python
from pathlib import Path,PurePath
import json
import re
import sys
import subprocess
import shlex
import logging
import redis

#REDIS_COMMAND = '/usr/local/webserver/redis/bin/redis-cli'
REDIS_DATA_PATH = '/data0/redis'

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='/data0/logs/zabbix_agent/redis.log',
                filemode='a')

class Monitor(object):
    '''监控redis状态'''
    def __init__(self, redis_data_path, port=None):
        self.redis_data_path = redis_data_path
        self.port = port

    def discover(self):
        '''发现所有的redis实例'''
        ports = [ {'{#REDISPORT}':PurePath(d).name} for d in Path(self.redis_data_path).glob('*') if d.is_dir() and re.fullmatch('[1-5]?[0-9]{1,4}', PurePath(d).name) ]
        print(json.dumps({'data':ports},sort_keys=True,indent=4,separators=(',',':')))
    
    def __get_passwd(self):
        '''获取redis的密码'''
        with open('{0}/{1}/redis.conf'.format(self.redis_data_path, self.port), 'r') as f:
            for line in f:
                result = re.match(r'requirepass\s*"(.*)"', line)
                if result:
                    return result.group(1)
    
    def __get_key(self, cmd):
        '''获取redis的状态信息'''
        passwd = self.__get_passwd()
        r = redis.StrictRedis(host='127.0.0.1', port=self.port, password=passwd, db=0)
        try:
            return eval('r.{0}()'.format(cmd))
        except Exception as e:
            mes = '"{0}" PORT {1}'.format(e, self.port)
            logging.error(mes)
            return None
        finally:
            #关闭redis连接
            r = None

    def ping(self):
        '''检查redis是否存活'''
        result = self.__get_key('ping')
        if result:
            print(1)
        else:
            print(0)
 
    def info(self, key):
        '''获取redis对应信息'''
        result = self.__get_key('info')
        if result:
            print(result[key])
        else:
            print(result)

if __name__ == '__main__':
    if len(sys.argv) == 1: 
        monitor = Monitor(REDIS_DATA_PATH)
        monitor.discover()
    elif len(sys.argv) == 3:
        monitor = Monitor(REDIS_DATA_PATH, sys.argv[1])
        if sys.argv[2] == 'ping':
            monitor.ping()
        else:
            monitor.info(sys.argv[2])
    else:
        error_info = 'Error: Unknown Command Format!'
        print(error_info)
