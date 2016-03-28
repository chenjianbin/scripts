#!/bin/bash
DBUSERNAME='remote'
DBPASSWORD='qSDH@MoS'
DBAUTHDB='admin'
DATADIR='/data0/mongodb/'
cd /data0/scripts/backupmongo
for DBPORT in `ls -lh $DATADIR|awk -F\  '{print $9}'|grep -Po '[0-9]+$'`
do 
	grep -Po '^auth.*=.*true' $DATADIR/$DBPORT/mongod.conf >/dev/null
	if [ $? -eq 0 ]
	then
		./mongobackup.sh $DBPORT $DBUSERNAME $DBPASSWORD $DBAUTHDB
	else
		./mongobackup.sh $DBPORT
	fi
done
