#!/bin/bash
set -o nounset
set -o errexit

PORT=$1
REDIS_COMMAND=/usr/local/webserver/redis/bin
BASEDIR=/data0/redis/${PORT}
DATADIR=${BASEDIR}/data
LOGDIR=${BASEDIR}/logs

function gen_dir(){
if [ -e $BASEDIR ]
then
 echo "The $PORT instance is exist!"
else
 mkdir $DATADIR -p
 mkdir $LOGDIR -p
 gen_config
 gen_redisd
fi
}

function gen_redisd(){
cat >>${BASEDIR}/redisd <<EOF
#!/bin/bash
case \$1 in
"start")
        $REDIS_COMMAND/redis-server ${BASEDIR}/redis.conf;;
"stop")
        $REDIS_COMMAND/redis-cli -p $PORT shutdown;;
"restart")
        ${BASEDIR}/redisd stop
        ${BASEDIR}/redisd start;;
"*")
        echo "usage: ${BASEDIR}/redisd {start|stop|restart}";;
esac
EOF
chmod 755 ${BASEDIR}/redisd
}

function gen_config(){
cat >>${BASEDIR}/redis.conf<<EOF
daemonize yes
pidfile ${BASEDIR}/redis.pid
port $PORT
tcp-backlog 511
bind 127.0.0.1
timeout 0
tcp-keepalive 0
loglevel notice
logfile ${LOGDIR}/redis.log
databases 16
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir $DATADIR
maxmemory 256000000
slave-serve-stale-data yes
slave-read-only yes
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
slave-priority 100
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
latency-monitor-threshold 0
notify-keyspace-events ""
hash-max-ziplist-entries 512
hash-max-ziplist-value 64
list-max-ziplist-entries 512
list-max-ziplist-value 64
set-max-intset-entries 512
zset-max-ziplist-entries 128
zset-max-ziplist-value 64
hll-sparse-max-bytes 3000
activerehashing yes
client-output-buffer-limit normal 0 0 0
client-output-buffer-limit slave 256mb 64mb 60
client-output-buffer-limit pubsub 32mb 8mb 60
hz 10
aof-rewrite-incremental-fsync yes
EOF
}
gen_dir


