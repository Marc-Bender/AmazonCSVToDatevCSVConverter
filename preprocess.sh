#! /usr/bin/bash

infile=$1
outfile=$2

if [ -f $infile ]
then
	if [ -f $outfile ]
	then
		echo "Overwriting the Outfile is not yet supported"
	else
		cat $infile | 
			sed -r 's/\t/;/g' |
			cut -d\; -f7,12,31,53,54,63,66,68,69,79,83 |
			tee > $outfile
		# Tabelle1 equivalent generated
	fi
else
	echo "Infile not existing"
fi
