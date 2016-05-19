#!/usr/lib/env python
#-- coding:utf-8 --
import random
import urllib2
import time
import datetime

while True:
    now = datetime.datetime.now()
    nowhour = int(now.strftime('%H'))
    if 9 > nowhour > 1:
        randtime = random.randint(600,1800)
    else:
        #randtime = random.randint(1,3)
        randtime = 1
    try:
        urllib2.urlopen("http://www.zhangshangduobao.net/index.php/go/autolottery/auto_rand_duobao")
    finally:
        time.sleep(randtime)
