#!/usr/bin/env python
from pathlib import Path, PurePath
from subprocess import Popen, PIPE
from email.mime.text import MIMEText
from email.header import Header
import os
import re
import time
import smtplib
import shlex
import datetime
import urllib.request
import urllib.parse
import socket
import json

MYSQL_DIR = '/data0/mysql'
''' Backup_DataDir 千万别在根目录，否则会很悲催。'''
BACKUP_DATADIR = '/data1/backups/mysql'
MYSQL_DEFAULTS_FILE = ('/etc/my.cnf.d' if os.path.isdir('/etc/my.cnf.d') else '/etc/mysql/mysql.conf.d')
CLEAN_DAY = 5
MSG = ''

SLACK_URL = 'https://hooks.slack.com/services/TaaxxxCD5/B9xxx1X4J/oICgcpCBxxxAuRPGl4xGNQ'
SLACK_USERNAME = 'backups'
SLACK_CHANNEL = '#backups'


TELEGRAM_TOKEN = 'xxxx:AAG36djBjow7yxxxxxKYtC2qEMQIJBY'
TELEGRAM_CHAT_ID = '-xxxx'
TELEGRAM_URL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

def backup():
    global MSG
    MSG = f'{MSG}Host: {socket.gethostname()} Databases Backup\n'
    print(MSG)
    ports = sorted([ p.name for p in Path(MYSQL_DIR).glob('*') if p.is_dir() and re.fullmatch('[2-5]?[0-9]{1,4}', p.name) ])
    result_msg = {}
    for port in ports:
        if port == '3306':
            continue
        mysql_defaults_file = Path(MYSQL_DEFAULTS_FILE) / f'mysqld@{port}.cnf'
        backup_dir = Path(BACKUP_DATADIR) / port
        if mysql_defaults_file.is_file():
            if not backup_dir.exists():
                backup_dir.mkdir(parents=True)
            backup_file = str(backup_dir / f'{datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.xbstream')
            cmd1 = shlex.split(f'xtrabackup --defaults-file={MYSQL_DEFAULTS_FILE}/mysqld@{port}.cnf --backup --user=root --socket=/data0/mysql/{ port }/mysql.sock  --stream=xbstream --compress --target-dir=/tmp')
            with open(backup_file, 'wb') as f:
                child = Popen(cmd1, stdout=f)
                child.wait()
                if child.returncode:
                    MSG = f'{MSG}{port}: Backup Failed!\n'
                else:
                    MSG = f'{MSG}{port}: Backup Success!\n'
        else:
            MSG = f'{MSG}{port}: Not Found my.cnf!\n'
        
def clean():
    global MSG
    MSG = f'{MSG}清理过期备份\n'
    for f in Path(BACKUP_DATADIR).glob('**/*.xbstream'):
        if (f.stat().st_mtime + CLEAN_DAY * 24 * 3600) < time.time():
            MSG = f'{MSG}Clean {f} \n'
            f.unlink()

def email():
    global MSG
    sender = 'xxxxx'
    pwd = 'xxxxxxxxx'
    receivers = ['xxxxx@qq.com']
    message = MIMEText(MSG, 'html', 'utf-8')
    message['From'] = Header('send@xxxxxx.com', 'utf-8')
    message['To'] =  Header('tony', 'utf-8')
    message['Subject'] = Header('数据库备份报告', 'utf-8')

    try:
        smtpobj = smtplib.SMTP('smtp.exmail.qq.com')
        smtpobj.login(sender, pwd)
        smtpobj.sendmail(sender, receivers, message.as_string())
        print('邮件发送成功')
    except smtplib.SMTPException:
        print('Error: 无法发送邮件')
    
def slack():
    '''send backup messages to slack'''
#    global MSG
    url = 'https://hooks.slack.com/services/TaaK9CD5/B9XF61X4J/oICgcpCBccscPAuRPGl4xGNQ'
    username = 'backups'
    payload = { 'payload': { 'channel': SLACK_CHANNEL, 'username': SLACK_USERNAME, 'text': MSG, 'icon_emoji': ':smile:' } }
    req=urllib.request.Request(SLACK_URL, method='POST', data=urllib.parse.urlencode(payload).encode('utf-8'))
    try:
        with urllib.request.urlopen(req) as r:
           print(r.getcode())
    except urllib.error.URLError as e:
           print(e)
           
def telegram():
    '''send backup messages to telegram'''
    data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": MSG}).encode()
    
    req = urllib.request.Request(TELEGRAM_URL, data=data, method="POST")
    
    try:
        response = urllib.request.urlopen(req)
        result = json.loads(response.read())
        
        if result["ok"]:
            print("Message sent successfully")
        else:
            print(f"Failed to send message: {result}")
    except Exception as e:
        print(f"Failed to send message: {e}")

if __name__=='__main__':
    backup()
    clean()
    telegram()
#    slack()       
#   email()

