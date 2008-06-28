#!/bin/bash

CLIENT=/usr/local/google_appengine/tools/bulkload_client.py
URL=http://localhost:8080/loader
#URL=http://ipg.appspot.com/loader
COOKIE='dev_appserver_login="test@example.com:True"'

echo "Importing works"
$CLIENT --url=$URL --kind=Work --filename=data/works.csv --cookie=$COOKIE
echo "Importing books"
$CLIENT --url=$URL --kind=Book --filename=data/books.csv --cookie=$COOKIE
echo "Importing chapters"
$CLIENT --url=$URL --kind=Chapter --filename=data/chapters.csv --cookie=$COOKIE
echo "Importing verses"
$CLIENT --url=$URL --kind=Verse --filename=data/verses.csv --cookie=$COOKIE
