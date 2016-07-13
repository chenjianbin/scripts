#!/bin/bash

DIR=`dirname $0`
$DIR/sendEmail \
-f send@xxx.com \
-t $1 \
-s smtp.exmail.qq.com \
-u "$2" \
-o message-content-type=html \
-o message-charset=utf8 \
-xu send@xxx.com \
-xp xxxxxxxxxxxx \
-l sendEmail.log \
-m "$3"
