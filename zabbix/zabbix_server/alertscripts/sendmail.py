#!/usr/bin/env python3
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import sys
import datetime


class Email(object):
	def __init__(self, sender, sender_pwd, from_user, to_user, smtp_host='smtp.exmail.qq.com', receivers=[], subject='报告', message='报告详情'):
		self.sender = sender
		self.sender_pwd = sender_pwd
		self.smtp_host = smtp_host
		self.receivers = receivers
		self.from_user = from_user
		self.to_user = to_user
		self.subject = subject
		self.message = message

	def format_message(self):
		message = MIMEText(self.message, 'html', 'utf-8')
		message['From'] = Header(self.from_user, 'utf-8')
		message['To'] =  Header(self.to_user, 'utf-8')
		message['Subject'] = Header(self.subject, 'utf-8')
		return message.as_string()

	def send(self):
		message = self.format_message()
		time = str(datetime.datetime.now())
		log_message = '[{0}] receivers:{1} subject:{2} message:{3} '.format(time, self.receivers, self.subject, self.message)
		with open('sendmail.log', 'a') as logfile:
			try:
				smtpobj = smtplib.SMTP(self.smtp_host)
				smtpobj.login(self.sender, self.sender_pwd)
				smtpobj.sendmail(self.sender, self.receivers, message)
				log_message = log_message + 'status:发送成功'
			except smtplib.SMTPException as e:
				log_message = log_message + 'status:发送失败 info:{0}'.format(e)
			finally:
				logfile.writelines(log_message)


if __name__ == '__main__':
	receivers = []
	receivers.append(sys.argv[1])
	ins = Email(sender='send@wanjizhijia.com', sender_pwd='BOZfdV8O2zMuTStp', from_user='zabbix', to_user='运维负责人', smtp_host='smtp.exmail.qq.com', 
				receivers=receivers, subject=sys.argv[2], message=sys.argv[3])
	ins.send()
