#!/bin/bash
DATE=2016-11-08
ERROR_FILE=/data0/mysql/3306/logs/mysql-error.log
for table in `grep -P ${DATE}.*repaired  $ERROR_FILE |grep -oP \'.*\'|sed  "s#^'./##g"|sed "s#'##g"|sed "s#/#.#g"`
do 
    mysql --socket=/data0/mysql/3306/mysql.sock -e "repair table $table"
done
