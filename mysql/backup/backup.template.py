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

MYSQL_DIR = '/data0/mysql'
''' Backup_DataDir 千万别在根目录，否则会很悲催。'''
BACKUP_DATADIR = '/data0/backups/mysql'
CLEAN_DAY = 7
MAIL_MSG = ''

def backup():
	global MAIL_MSG
	MAIL_MSG = MAIL_MSG + '<h1>数据库备份</h1>'
	ports = [ PurePath(p).name for p in Path(MYSQL_DIR).glob('*') if p.is_dir() and re.match('[1-65535]', PurePath(p).name) ]
	result_msg = {}
	for port in ports:
		mysql_defaults_file = Path(MYSQL_DIR) / port / 'my.cnf'	
		backup_dir = Path(BACKUP_DATADIR) / port
		if mysql_defaults_file.is_file():
			if not backup_dir.exists():
				backup_dir.mkdir(parents=True)
			gz_file = str(backup_dir / (datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.tar.gz'))
			cmd1 = shlex.split('innobackupex --defaults-file=/data0/mysql/%s/my.cnf --user=root --socket=/data0/mysql/%s/mysql.sock  --stream=tar /tmp/' % (port, port))
			with open(gz_file, 'wb') as f:
				child1 = Popen(cmd1, stdout=PIPE)
				child2 = Popen('gzip', stdin=child1.stdout, stdout=f)
				child2.wait()
				child1.wait()
				if child1.returncode or child2.returncode:
					MAIL_MSG = MAIL_MSG + '<p>%s : Backup Failed!</p>' % port
				else:
					MAIL_MSG = MAIL_MSG + '<p>%s : Backup Success!</p>' % port
		else:
			MAIL_MSG = MAIL_MSG + '<p>%s : Not Found my.cnf!</p>' % port
		
def clean():
	global MAIL_MSG
	MAIL_MSG = MAIL_MSG + '<h1>清理过期备份</h1>'
	for f in Path(BACKUP_DATADIR).glob('**/*.tar.gz'):
		if (f.stat().st_mtime + CLEAN_DAY * 24 * 3600) < time.time():
			MAIL_MSG = MAIL_MSG + '<p>Clean %s </p>' % str(f)
			f.unlink()

def email():
	global MAIL_MSG
	sender = 'send@wanjizhijia.com'
	pwd = 'xxxxxxxxx'
	receivers = ['546391242@qq.com']
	message = MIMEText(MAIL_MSG, 'html', 'utf-8')
	message['From'] = Header('send@wanjizhijia.com', 'utf-8')
	message['To'] =  Header('Bice.', 'utf-8')
	message['Subject'] = Header('数据库备份报告', 'utf-8')

	try:
		smtpobj = smtplib.SMTP('smtp.exmail.qq.com')
		smtpobj.login(sender, pwd)
		smtpobj.sendmail(sender, receivers, message.as_string())
		print('邮件发送成功')
	except smtplib.SMTPException:
		print('Error: 无法发送邮件')
	
if __name__=='__main__':
	backup()
	clean()
	email()

