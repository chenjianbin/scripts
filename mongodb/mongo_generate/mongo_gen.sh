#!/bin/bash
set -o nounset
set -o errexit

PORT=$1
BASEDIR=/data0/mongodb/${PORT}
DATADIR=${BASEDIR}/data
LOGDIR=${BASEDIR}/logs
SCRIPTS_DIR=`dirname $0`

function gen_dir(){
if [ -e $BASEDIR ]
then
 echo "The $PORT instance is exist!"
else
 mkdir -p $DATADIR
 mkdir -p $LOGDIR
 cp $SCRIPTS_DIR/mongod  $BASEDIR
 sed -i "18,18 s#\/data1\/mongodb\/99999/mongod.conf#`echo $BASEDIR`\/mongod.conf#g" ${BASEDIR}/mongod
 gen_config
 chown mongod.mongod $BASEDIR -R
fi
}

function gen_config(){
cat >>${BASEDIR}/mongod.conf <<EOF 
### GENERAL ###
bind_ip = 127.0.0.1
port    = $PORT
pidfilepath      = ${BASEDIR}/mongod.pid
unixSocketPrefix = $BASEDIR
fork             = true

### DATA STORAGE ###
dbpath          = $DATADIR
directoryperdb  = true
journal = true

### LOG ###
oplogSize = 1024
# QUERY LOG #
logpath         = ${LOGDIR}/mongodb.log
logappend       = true

# SLOWLOG #
profile          = 0 
#slowms  = 1000

### LIMITS ###
maxConns        = 20000

### SAFETY ###
#auth = true
#noauth = true

### REPLICATION ###
#replSet                = repl
#master           = true
slave           = true
source          = 0.0.0.0:0
autoresync      = true
#keyFile        =
EOF
}

gen_dir