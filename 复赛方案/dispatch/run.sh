#!/usr/bin/env bash

## Specify $JAVA_HOME as you need.
if [ -z "$JAVA_HOME" ] ; then
  JAVA_HOME="/data/jdk11.0.2"
fi

echo $JAVA_HOME

cd /data

cpu=8
GC_PARALLEL_THREAD=`expr $((cpu*5/8))`
GC_CONC_THREAD=`expr $((cpu*5/8/4+1))`

MEM_OPTS="-server"

G1_OPTS="-XX:+UnlockExperimentalVMOptions -XX:G1RSetUpdatingPauseTimePercent=5 -XX:InitiatingHeapOccupancyPercent=33 -XX:G1NewSizePercent=35 -XX:G1MaxNewSizePercent=50 -XX:+AlwaysPreTouch -XX:-ParallelRefProcEnabled"
G1_OPTS="$G1_OPTS -XX:ParallelGCThreads=$GC_PARALLEL_THREAD -XX:ConcGCThreads=$GC_CONC_THREAD"
G1_OPTS="$G1_OPTS -XX:ReservedCodeCacheSize=128m -XX:+PrintCodeCache"

$JAVA_HOME/bin/java $MEM_OPTS $G1_OPTS -jar dispatch-demo.jar 2>&1 &
