#!/bin/bash

DBFILE="db_test.json"
if [ -f $DBFILE ] ; then
  rm $DBFILE && python3 main.py && cat $DBFILE
else
  python3 main.py && cat $DBFILE
fi

