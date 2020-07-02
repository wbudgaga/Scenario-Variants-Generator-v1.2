if [ $# -ne 2 ] ; then
	echo "Enter the range(start-end) of machines you want remove stored scenarios from"
	exit 1
fi
host="lattice-"
i="$1"
while [ $i -le "$2" ]
do
   h1="$host$i"
   echo "Removing scenarios from machine $h1"
   ssh $h1 "rm  /s/${h1}/a/tmp/scenarios/*"
   i=$(( i + 1 ))
done
