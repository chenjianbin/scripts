#!/bin/bash
TIME=`/usr/local/webserver/mysql/bin/mysql -u root -S /data0/mysql/$1/mysql.sock -e "show slave status\G"|grep -P 'Seconds_Behind_Master'|awk -F\: '{print $2}'|sed s/[[:space:]]//g`
if [ $TIME == 'NULL' ]
then 
    TIME=10000
fi
echo $TIME
