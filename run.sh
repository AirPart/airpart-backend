#!/bin/bash

DBFILE="db_test.json"
if [ -f $DBFILE ] ; then
  rm $DBFILE && python3 main.py
else
  python3 main.py
fi

pip freeze > requirement.txt
