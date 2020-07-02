if [ $# -ne 2 ] ; then
	echo "You have to enter the start & end of variants you want to compress"
	exit 1
fi

i="$1"
cd /run/media/wbudgaga/My\ Passport/Walid/1million_Texas_variants/

pwd
while [ $i -le "$2" ]
do
	h1="scenario_$i.xml"
	bzip2 $h1 
	i=$(( i + 1 ))
done
