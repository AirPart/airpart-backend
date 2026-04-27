#!/bin/bash

DBFILE="data/test/db_test.json"
DBIMAGE="data/test/product_image/"

rm -rf $DBFILE $DBIMAGE
python3 main.py

pip freeze > requirement.txt
