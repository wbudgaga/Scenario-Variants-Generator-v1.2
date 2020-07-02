if [ $# -ne 1 ] ; then
	echo "You have to enter number of used machines"
	exit 1
fi
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
for i in $(cat ${script_dir}/clusterNodes.txt)
do
        ml[$t]=$(echo $i | tr -d '\r')
        t=$((t+1))
        # echo "$i"
done
i=0
while [ $i -lt "$1" ]
do
	h1=${ml[i]}
#	ssh $h1 "ls -lt /s/$h1/a/tmp/wbudgaga/iowa/scenarios/ | wc -l"
	ssh $h1  rsync -avz /s/$h1/a/tmp/wbudgaga/iowa/scenarios/* coconuts:/s/coconuts/a/tmp/wbudgaga/iowa/
i=$(( i + 1 ))
done
