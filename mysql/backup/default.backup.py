#!/usr/bin/env python
from pathlib import Path, PurePath
from subprocess import Popen, PIPE
from email.mime.text import MIMEText
from email.header import Header
import re
import time
import smtplib
import shlex
import datetime
import urllib.request
import urllib.parse
import socket

MYSQL_DIR = '/data0/mysql'
''' Backup_DataDir 千万别在根目录，否则会很悲催。'''
BACKUP_DATADIR = '/data1/backups/mysql'
CLEAN_DAY = 7
MSG = ''

def backup():
    global MSG
    MSG = MSG + 'Host: ' + socket.gethostname() + ' Databases Backup\n'
    ports = sorted([ p.name for p in Path(MYSQL_DIR).glob('*') if p.is_dir() and re.fullmatch('[2-5]?[0-9]{1,4}', p.name) ])
    result_msg = {}
    for port in ports:
        mysql_defaults_file = Path('/etc/my.cnf.d') / 'mysqld@{}.cnf'.format(port)
        backup_dir = Path(BACKUP_DATADIR) / port
        if mysql_defaults_file.is_file():
            if not backup_dir.exists():
                backup_dir.mkdir(parents=True)
            backup_file = str(backup_dir / (datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.xbstream'))
            cmd1 = shlex.split('xtrabackup --defaults-file=/etc/my.cnf.d/mysqld@{0}.cnf --backup --user=root --socket=/data0/mysql/{0}/mysql.sock  --stream=xbstream --compress --target-dir=/tmp'.format(port))
            with open(backup_file, 'wb') as f:
                child = Popen(cmd1, stdout=f)
                child.wait()
                if child.returncode:
                    MSG = MSG + port + ' : Backup Failed!\n'
                else:
                    MSG = MSG + port + ' : Backup Success!\n'
        else:
            MSG = MSG + port + ' : Not Found my.cnf!\n'
        
def clean():
    global MSG
    MSG = MSG + '清理过期备份\n'
    for f in Path(BACKUP_DATADIR).glob('**/*.tar.gz'):
        if (f.stat().st_mtime + CLEAN_DAY * 24 * 3600) < time.time():
            MSG = MSG + 'Clean {} \n'.format(str(f))
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
    global MSG
    url='https://hooks.slack.com/services/TaaK9CD5/B9XF61X4J/oICgcpCBccscPAuRPGl4xGNQ'
    username='backups'
    payload={ 'payload': { 'channel': '#backups', 'username': username, 'text': MSG, 'icon_emoji': ':smile:' } }
    req=urllib.request.Request(url, method='POST', data=urllib.parse.urlencode(payload).encode('utf-8'))
    try:
        with urllib.request.urlopen(req) as r:
           print(r.getcode())
    except urllib.error.URLError as e:
           print(e)

if __name__=='__main__':
    backup()
    clean()
    slack()       
#   email()

