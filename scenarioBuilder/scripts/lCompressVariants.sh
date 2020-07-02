if [ $# -ne 3 ] ; then
	echo "You have to enter the machineNumber you want compress files on, start & end scenario index"
	exit 1
fi

i="$2"

host="lattice-$1"

sDir="/s/$host/a/tmp/wbudgaga"
dstDir="${sDir}/c_${host}"
mkdir  ${dstDir}
srcDir="${sDir}/scenarios_oldV"

while [ $i -le "$3" ]
do
	h1="${srcDir}/scenario_$i.xml" 
	h2="${dstDir}/scenario_$i.xml.bz2"
	bzip2 -ck $h1 > $h2
	i=$(( i + 1 ))
done
