if [ $# -ne 3 ] ; then
	echo "You have to enter the intermidate folder! and the machines[start end]"
	exit 1
fi
host="lattice-"
i="$2"
while [ $i -le "$3" ]
do
   h1="$host$i" 
   echo "Copying scenarios from '$h1 (dir:/tmp/scenarios/*) to ${1}/"
   ssh $h1 "cp -r /tmp/scenarios/* ${1}"
   mv ${1}/* /s/red-rock/a/nobackup/budgaga/scenarios/ 
   i=$(( i + 1 ))
done
