#!/usr/bin/env bash

## Specify $JAVA_HOME as you need.
if [ -z "$JAVA_HOME" ] ; then
  JAVA_HOME="/data/jdk-11.0.2"
fi
export JAVA_HOME
cd dispatch-demo-py

export FLASK_APP=app.py
flask run -p 8080 &





