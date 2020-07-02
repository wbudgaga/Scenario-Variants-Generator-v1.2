if [ $# -ne 5 ] ; then
        echo "Please enter [Scenario] [ParamRanges] [chunckNumber] [chunckSize] [workDir]"
        exit 1
fi
script_dir=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
############ load the hosts from the given file, clusterNodes.txt.#####################
t=0
for i in $(cat ${script_dir}/clusterNodes.txt)
do
        ml[$t]=$(echo $i | tr -d '\r')
        t=$((t+1))
        # echo "$i"
done
#######################################################################################
processesOnEachMachine=4
machineNum=$(( ${3} / processesOnEachMachine ))
working_dir=${5}
host=${ml[machineNum]}

ssh $host  "mkdir -p /s/$host/a/tmp/$working_dir/lhs"
scp /s/$HOSTNAME/a/tmp/$working_dir/lhs/samples_${3}.lhs  $host:/s/${host}/a/tmp/$working_dir/lhs/
echo "Assigning the chunck#:$3 of size:$4 to machine ${host}  $machineNum"
#ls -lt ${working_dir}/scenarioBuilderTask.sh 
ssh $host "bash ${script_dir}/scenarioBuilderTask.sh $1 $2 $3 $4 $working_dir" &
