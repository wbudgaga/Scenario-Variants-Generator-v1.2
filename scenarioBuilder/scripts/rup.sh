if [ $# -ne 2 ] ; then
	echo "Enter the range(start-end) of machines you want check the load"
	exit 1
fi
host="lattice-"
i="$1"
while [ $i -le "$2" ]
do
   h1="$host$i"
   rup $h1
   i=$(( i + 1 ))
done
