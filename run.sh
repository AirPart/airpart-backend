#!/bin/bash

DBFILE="data/test/db_test.json"
DBIMAGE="static/test/product_image/"
DBDOCS="static/test/product_document/"

rm -rf $DBFILE $DBIMAGE $DBDOCS
python3 main.py

pip freeze > requirement.txt
