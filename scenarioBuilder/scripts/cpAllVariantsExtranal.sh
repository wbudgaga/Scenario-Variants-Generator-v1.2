if [ $# -ne 2 ] ; then
	echo "You have to enter the machines[start end]"
	exit 1
fi
host="lattice-"
i="$1"
src="/run/media/wbudgaga/My\ Passport/Walid/1million_Texas_variants/"
while [ $i -le "$2" ]
do
h1="$host$i"
d="/s/$h1/a/tmp/scenarios/*"
echo "Copying scenarios  ($h1:$d ${src})"
rsync -avz  $h1:/s/$h1/a/tmp/scenarios/* /run/media/wbudgaga/My\ Passport/Walid/1million_Texas_variants/ 
i=$(( i + 1 ))
done
