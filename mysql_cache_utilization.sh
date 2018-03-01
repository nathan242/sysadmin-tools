#!/bin/bash

MYSQL=mysql

function help
{
	echo "Check MySQL/MariaDB query cache utilization."
	echo "USAGE: $0 [SOCKET] [USER] (optional)[PASSWORD]"
}

if [ $# -gt 3 ]
then
	echo "Too many arguments!"
	help
	exit 1
fi

if [ $# -lt 2 ]
then
	echo "Not enough arguments!"
	help
	exit
fi

SOCKET=$1
USER=$2
if [ $# -eq 3 ]
then
	PASS=$3
fi

if [ $# -eq 3 ]
then
	MYSQLSTRING="$MYSQL -A --socket=${SOCKET} -u $USER -p${PASS}"
else
	MYSQLSTRING="$MYSQL -A --socket=${SOCKET} -u $USER -p"
fi

QUERY_CACHE_SIZE=`echo "show global variables like 'query_cache_size'" | $MYSQLSTRING | grep query_cache_size`
QCACHE_HITS=`echo "show global status like 'Qcache_hits'" | $MYSQLSTRING | grep Qcache`
QCACHE_INSERTS=`echo "show global status like 'Qcache_inserts'" | $MYSQLSTRING | grep Qcache`
QCACHE_NOT_CACHED=`echo "show global status like 'Qcache_not_cached'" | $MYSQLSTRING | grep Qcache`
QCACHE_LOWMEM_PRUNES=`echo "show global status like 'Qcache_lowmem_prunes'" | $MYSQLSTRING | grep Qcache`
QCACHE_FREE_MEMORY=`echo "show global status like 'Qcache_free_memory'" | $MYSQLSTRING | grep Qcache`
COM_SELECT=`echo "show global status like 'Com_select'" | $MYSQLSTRING | grep Com`

QUERY_CACHE_SIZE=`echo $QUERY_CACHE_SIZE | cut -d' ' -f2`
QCACHE_HITS=`echo $QCACHE_HITS | cut -d' ' -f2`
QCACHE_INSERTS=`echo $QCACHE_INSERTS | cut -d' ' -f2`
QCACHE_NOT_CACHED=`echo $QCACHE_NOT_CACHED | cut -d' ' -f2`
QCACHE_LOWMEM_PRUNES=`echo $QCACHE_LOWMEM_PRUNES | cut -d' ' -f2`
QCACHE_FREE_MEMORY=`echo $QCACHE_FREE_MEMORY | cut -d' ' -f2`
COM_SELECT=`echo $COM_SELECT | cut -d' ' -f2`
UTILIZATION=`echo "scale=2; $QCACHE_HITS/($COM_SELECT+$QCACHE_HITS)*100" | bc`
CACHE_USED=`echo "scale=2; (($QUERY_CACHE_SIZE-$QCACHE_FREE_MEMORY)/$QUERY_CACHE_SIZE)*100" | bc`
HIT_RATE=`echo "scale=2; ($QCACHE_HITS/($QCACHE_HITS+$QCACHE_INSERTS+$QCACHE_NOT_CACHED))*100" | bc`
HTPR=`echo "scale=2; $QCACHE_INSERTS/$QCACHE_LOWMEM_PRUNES" | bc`

echo "=== MYSQL CACHE UTILIZATION ==="
echo "Query_cache_size: $QUERY_CACHE_SIZE"
echo "Com_select: $COM_SELECT"
echo "Qcache_hits: $QCACHE_HITS"
echo "Qcache_inserts: $QCACHE_INSERTS"
echo "Qcache_not_cached: $QCACHE_NOT_CACHED"
echo "Qcache_free_memory: $QCACHE_FREE_MEMORY"
echo "Qcache_lowmem_prunes: $QCACHE_LOWMEM_PRUNES"
echo
echo "Cache Utilization: $UTILIZATION%"
echo "Cache Used: $CACHE_USED%"
echo "Hit Rate: $HIT_RATE%"
echo "Insert To Prune Ratio: $HTPR"
