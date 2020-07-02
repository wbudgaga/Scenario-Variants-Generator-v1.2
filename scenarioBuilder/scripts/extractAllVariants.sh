if [ $# -ne 2 ] ; then
	echo "Enter the range(start-end) of machines you want extract variants on"
	exit 1
fi
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

host="lattice-"
i="$1"
c=20
t=0
while [ $i -le "$2" ]
do
   k=$i
   h="$host$i"
   if [ $i == 30 ] ;  then
	h="lattice-19"
	k=19
   fi

   if [ $i == 31 ] ;  then
	h="lattice-20"
	k=20
   fi

   sn=$(( t * c + 1 ))
   t=$(( t + 1 ))
   en=$(( t * c ))
   #echo " $k  $sn  $en" 
   ssh $h "bash  ${script_dir}/variantExtractor.sh $sn  $en" &
   i=$(( i + 1 ))

done
