if [ $# -ne 2 ] ; then
	echo "You have to enter the machines[start end]"
	exit 1
fi
host="lattice-"
i="$1"
while [ $i -le "$2" ]
do
   h1="$host$i" 
   echo "${h1}:"
   #ssh $h1  "ls -l /s/$h1/a/tmp//wbudgaga/c_lattice-$i/ | wc -l"
    ssh $h1  "ls -l /s/$h1/a/tmp//wbudgaga/scenarios_oldV/ | wc -l"
	#ssh $h1  "pkill -f scenarioBuilderTask.py"
   i=$(( i + 1 ))
done
