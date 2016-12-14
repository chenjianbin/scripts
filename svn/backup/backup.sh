#!/bin/bash
SVNDIR=/data0/svn
BACKDIR=/data0/backups/svn
LOGFILE=/data0/logs/svn/svn_backup.log

R_ADDR=192.168.1.240
R_BACKDIR=/data0/backups/


function backup(){
    for repo in `find $SVNDIR -maxdepth 1 -mindepth 1 -type d -exec basename {} \;`
    do
        DAY_BACKDIR=$BACKDIR/$repo.$(date +%F)
        if [ ! -e `dirname $LOGFILE` ]
		then 
			mkdir -p `dirname $LOGFILE`
		fi
        if [ -e $DAY_BACKDIR ]
        then
            echo "$DAY_BACKDIR is exists" >> $LOGFILE
        else
            mkdir -p $DAY_BACKDIR
            svnadmin hotcopy $SVNDIR/$repo $DAY_BACKDIR && echo "[`date +%F`] $repo backup success !" >> $LOGFILE
        fi
    done
}

function clean(){
    find $BACKDIR -maxdepth 1 -mindepth 1 -type d  -mtime +5 -exec rm -rf {} \;
}

function sync(){
    rsync -avP --delete $BACKDIR  $R_ADDR:$R_BACKDIR
}

backup
clean
sync
