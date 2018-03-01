#!/bin/bash

TASKS=`ps auxf | grep httpd | grep -v grep | wc -l`
SOCKETS_ESTAB=`netstat -tunp | grep httpd | grep ESTAB | wc -l`
SOCKETS_WAIT=`netstat -tunp | grep httpd | grep TIME_WAIT | wc -l`
SOCKETS_FIN=`netstat -tunp | grep httpd | grep FIN | wc -l`
SOCKETS_LISTEN=`netstat -tunpl | grep httpd | wc -l`

echo "HTTPD PROCESSES: $TASKS  SOCKETS -- ESTAB: $SOCKETS_ESTAB  WAIT: $SOCKETS_WAIT  FIN: $SOCKETS_FIN  LISTEN: $SOCKETS_LISTEN"

DEF_SORT="sort -nrk 5"
SORT="$DEF_SORT"

if [ $# -eq 1 ]
then
	case "$1" in
		-cpu)
			SORT="sort -nrk 5"
			;;
		-ss)
			SORT="sort -nrk 6"
			;;
		-m)
			SORT="sort -rk 4"
			;;
		-acc)
			SORT="sort -nrk 3"
			;;
		-pid)
			SORT="sort -nrk 2"
			;;
		-srv)
			SORT="sort -nrk 1"
			;;
	esac
fi

if [ $# -eq 2 ]
then
	OUTPUT=`apachectl fullstatus | sed -n -e '/^Srv/,$p' | sed -e '/^\ \ \ \ \ --/,$d' | grep -v OPTIONS | sed 1d | $SORT | grep $2`
else
	OUTPUT=`apachectl fullstatus | sed -n -e '/^Srv/,$p' | sed -e '/^\ \ \ \ \ --/,$d' | grep -v OPTIONS | sed 1d | $SORT`
fi

echo "Srv    PID   Acc          M CPU   SS   Req  Conn   Child Slot  Client          VHost                      Request"
echo "$OUTPUT"

