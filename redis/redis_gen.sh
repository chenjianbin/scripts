#!/bin/bash
set -o nounset
set -o errexit

PORT=$1
BASEDIR=/usr/local/webserver/redis
INSTANCEDIR=/data0/redis/${PORT}
DATADIR=${INSTANCEDIR}/data
LOGDIR=${INSTANCEDIR}/logs
PASSWD=`openssl rand -base64 20`

function gen_dir(){
if [ -e $INSTANCEDIR ]
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
cat >>${INSTANCEDIR}/redisd <<EOF
#!/bin/bash
# chkconfig: 2345 50 30
#
# description: Redis service
#
#Script:Redis command
 
Redisserver=$BASEDIR/bin/redis-server
Rediscli=$BASEDIR/bin/redis-cli
Redisconf=$INSTANCEDIR/redis.conf
 
function_start()
{
    printf "start redis-server..."
    \$Redisserver \$Redisconf &>/dev/null  & 
    if [ \$? -eq 0 ];then
        echo "runing"
    fi
}
 
function_stop()
{
    printf "stop redis-server..."
    \$Rediscli -p $PORT -a "$PASSWD" shutdown
    if [ \$? -eq 0 ];then
        echo "stop"
    fi
}
 
function_restart()
{
    function_start
    function_stop
}
 
function_kill()
{
    killall redis-server
}
 
function_status()
{
    a=\`ps -A|grep "redis-server\\>" -c\`
    if [ \$a -ge 1 ];then
        echo -e "The Redis is [\\e[0;32;5m runing \\e[0m]"
    else
        echo -e "The Redis is [\\e[0;31;5m not run \\e[0m]"
    fi
}
 
case "\$1" in
        start)
                function_start
                ;;
        stop)
                function_stop
                ;;
        restart)
                function_stop
                function_start
                ;;
        kill)
                function_kill
                ;;
        status)
                function_status
                ;;
              *)
              echo "Usage: /etc/init.d/redis {start|stop|restart|kill|status}"
             
esac
 
exit
EOF
chmod 700 ${INSTANCEDIR}/redisd
}

function gen_config(){
cat >>${INSTANCEDIR}/redis.conf<<EOF
################################## INCLUDES ###################################
################################ GENERAL  #####################################
daemonize yes
pidfile ${INSTANCEDIR}/redis.pid
bind 127.0.0.1
port $PORT
requirepass "$PASSWD"
tcp-backlog 511
timeout 0
tcp-keepalive 60
loglevel notice
logfile ${LOGDIR}/redis.log
databases 16
# unixsocket /tmp/redis.sock
# unixsocketperm 700
# syslog-enabled no
# syslog-ident redis
# syslog-facility local0
################################ SNAPSHOTTING  ################################
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir $DATADIR
################################# REPLICATION #################################
# slaveof 192.168.1.1 6379
# masterauth "xxxxxx"
slave-serve-stale-data yes
slave-read-only yes
slave-priority 100
repl-diskless-sync no
repl-diskless-sync-delay 5
repl-disable-tcp-nodelay no
################################### LIMITS ####################################
maxclients 10000
maxmemory 256000000
# maxmemory-policy allkeys-lru
# maxmemory-samples 5
############################## APPEND ONLY MODE ###############################
appendonly no
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb
aof-load-truncated yes
################################ LUA SCRIPTING  ###############################
lua-time-limit 5000
################################## SLOW LOG ###################################
slowlog-log-slower-than 10000
slowlog-max-len 128
################################ LATENCY MONITOR ##############################
latency-monitor-threshold 0
############################# EVENT NOTIFICATION ##############################
notify-keyspace-events ""
############################### ADVANCED CONFIG ###############################
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


