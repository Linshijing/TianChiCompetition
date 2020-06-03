#!/usr/bin/env bash
## Specify $JAVA_HOME as you need.
if [ -z "$JAVA_HOME" ] ; then
  JAVA_HOME="/data/jdk11.0.2"
fi

echo $JAVA_HOME

$JAVA_HOME/bin/java -server -Xms1g -Xmx1g -jar dispatch-judge-jar-with-dependencies.jar "$MOCK_DATA_DIR" "$API_SERVER"
