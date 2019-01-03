#!/bin/sh

set -e

PREFIX="download"

mksql()
{
	DB=$1

	rm -f $DB

	sqlite3 -batch $DB <<EOF
CREATE TABLE components (
	name	text NOT NULL PRIMARY KEY,
	producer_code	text NOT NULL,
	price	integer
);
EOF
}

for SECTION in $(cat SECTIONS); do

	DBFILE=$PREFIX/$SECTION.db

	if [ ! -f $DBFILE ]; then
		mksql $DBFILE

		for i in $PREFIX/$SECTION/$SECTION*; do
			./parse-one-file.py $DBFILE "$i"
		done
	fi

	echo
	echo "=== $SECTION ==="
	sqlite3 -separator " " $DBFILE "SELECT price, name, producer_code from components ORDER BY price;"
done
