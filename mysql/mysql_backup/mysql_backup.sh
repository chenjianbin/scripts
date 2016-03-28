#!/bin/bash
set -o nounset
set -o errexit

Mysql_User=remote
Mysql_Pwd=a2bsdciEyMq9DkKo
Mysql_Host=127.0.0.1
Mysql_Dir=/data0/mysql
#Backup_DataDir 千万别在根目录，否则会很悲催。
Backup_DataDir=/data0/mysql_backup

for Mysql_Port in `ls -l $Mysql_Dir|grep ^d|awk -F\  '{print $9}'`
do
	Mysql_Defaults_File=$Mysql_Dir/$Mysql_Port/my.cnf
	
	if [ -f $Mysql_Defaults_File ]
	then
		if [ ! -d $Backup_DataDir/$Mysql_Port ]
		then
			mkdir -p $Backup_DataDir/$Mysql_Port
		fi				
		innobackupex --defaults-file=$Mysql_Defaults_File --user=$Mysql_User --password=$Mysql_Pwd --host=$Mysql_Host --port=$Mysql_Port --rsync --stream=tar /tmp/|gzip >$Backup_DataDir/$Mysql_Port/`date +%F_%H-%M-%S`.tar.gz
		find $Backup_DataDir/$Mysql_Port -mtime +7 -type f -exec rm -f {} \;
	fi
done