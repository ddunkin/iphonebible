#!/bin/bash

CLIENT=/usr/local/google_appengine/tools/bulkload_client.py
URL=http://localhost:8080/loader
COOKIE='dev_appserver_login="test@example.com:True"'

echo "Importing works"
$CLIENT --url=$URL --kind=Work --filename=works.csv --cookie=$COOKIE
echo "Importing books"
$CLIENT --url=$URL --kind=Book --filename=books.csv --cookie=$COOKIE
echo "Importing chapters"
$CLIENT --url=$URL --kind=Chapter --filename=chapters.csv --cookie=$COOKIE
echo "Importing verses"
$CLIENT --url=$URL --kind=Verse --filename=verses.csv --cookie=$COOKIE
