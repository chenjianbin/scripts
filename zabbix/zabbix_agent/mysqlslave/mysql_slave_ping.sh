#!/bin/bash
STATUS=`/usr/local/webserver/mysql/bin/mysql -u root -S /data0/mysql/$1/mysql.sock -e "show slave status\G"|grep -P '(Slave_IO_Running|Slave_SQL_Running)'|grep 'Yes'|wc -l`
if [ $STATUS == '2' ]
then	
	echo 1
else
	echo 0
fi

