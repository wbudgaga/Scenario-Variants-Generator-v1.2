#!/bin/bash
if [ $# -ne 5 ] ; then
	echo "Please enter [Scenario] [ParamRanges] [chunckNumber] [chunckSize] [workDir]"
	exit 1
fi
host="lattice-"
echo "Running the scenarioBuilder on $(hostname), applying to chunck ${3}, in work dir ${5}"
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${script_dir}
cd ..
nice -19 python scenarioBuilderTask.py "$1" "$2" "$3"  "$4" "$5"
echo "======================================================================="


