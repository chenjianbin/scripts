#!/bin/bash
set -o nounset
set -o errexit 
CONFIG="`dirname $0`/config"
source $CONFIG

function dump() {
	mysqldump -u $SRC_USER -p$SRC_PASSWD -h $SRC_HOST -P $SRC_PORT $DBNAME >$BACKUP_DIR/$DBNAME.sql
}

function load() {
	mysql -C -u $SRC_USER -p$DEST_PASSWD -h $DEST_HOST -P $DEST_PORT $DBNAME <$BACKUP_DIR/$DBNAME.sql
}

function clearsqlfile() {
}

function main() {
	dump
	load
}

main
