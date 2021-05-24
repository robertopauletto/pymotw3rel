#! /bin/bash

FILE=/dati/dev/python/pymotw3restyling/dumpscripts/todo.db

if test -f "$FILE"; then
  rm "$FILE"
fi
