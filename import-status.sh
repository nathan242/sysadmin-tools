#!/bin/bash

if [ $# -ne 1 ]
then
	echo "Show import status for mysql/mariadb"
	echo "USAGE: $0 [import mysql PID]"
	exit
fi

if echo $1 | egrep -q '^[0-9]+$'
then

	PID=$1
	FILE=`ls -l /proc/$PID/fd/0 | tr -s ' ' | cut -d' ' -f11`

	FILESIZE=`ls -l $FILE | tr -s ' ' | cut -d' ' -f5`
	FILEPOS=`cat /proc/$PID/fdinfo/0 | grep pos | sed 's/\t/ /' | cut -d' ' -f2`

	PROGRESS=`echo "scale=4; ($FILEPOS/$FILESIZE)*100" | bc`

	echo "FILE: $FILE"
	echo "PROGRESS: $PROGRESS"

else
	echo "ERROR: PID must be an integer"
fi
