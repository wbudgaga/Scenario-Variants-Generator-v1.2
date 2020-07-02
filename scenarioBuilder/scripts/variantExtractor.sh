#!/bin/bash
if [ $# -ne 2 ] ; then
	echo "You have to enter start- & end-Variant "
	exit 1
fi
ExecDir="$HOME/python/workspace/scenarioAnalyicsFW/testing"
cd $ExecDir
nice -19 python extractVariants.py $1 $2
