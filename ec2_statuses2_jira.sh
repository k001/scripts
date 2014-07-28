!/bin/bash -
#title          :ec2_statuses2_jira.sh
#description    :
#author         :Ivan Zenteno
#email          :'ivan_dot_zenteno_at_zentenoit_dot_com'
#date           :2014-07-28
#version        :0.0.1
#usage          :./ec2_statuses2_jira．sh
#notes          :
#bash_version   :3.2.51(1)-release
#============================================================================


PROFILES=`sed -rn 's/^\[profile ([a-z\-]*)\]$/\1/p' $HOME/.aws/config`

HOME_PATH='/usr/local/etc/AWS_EC_CHECK'
#Adding home directory for work
if [ ! -d $HOME_PATH ]; then
    mkdir -p $HOME_PATH
fi;

#Definition for backup path
BACKUP_PATH=$HOME_PATH'/backups'
if [ ! -d $BACKUP_PATH ]; then
    mkdir -p $BACKUP_PATH;
fi;

#Working on home path
cd $HOME_PATH

#Definition for current and backup file
YESTERDAY=`date +%F -d '1 day ago'`
BACKUP_FILE="$BACKUP_PATH/$YESTERDAY.csv"
CURRENT_FILE='current.csv'
TMP=$HOME_PATH

#Now checking all the account instances status
#
# TODOs
# * Need other way to get this info (profile alias), the AWS ID and AWS SECRECT plain don't like me
#

cd $HOME_PATH
for account in $PROFILES; do
    if [ ! -d $account ]; then
        mkdir $account;
    fi;

    TMP_FILE="$TMP/$account/$CURRENT_FILE";
    ACCOUNT_JSON="$account.json"

    #backup the current file is already exists
    #if [ -f $CURRENT_FILE ]; then
    #    mv $CURRENT $BACKUP_FILE;
    #else
    #    touch $CURRENT_FILE
    #fi;

    cd $account;
    aws --profile $account ec2 describe-instance-status --query 'InstanceStatuses[*].{AZ:AvailabilityZone,ID:InstanceId,CODE:Events[0].Code,DATE:Events[0].NotBefore,DESC:Events[0].Description}' --filters "Name=event.code,Values=instance-retirement,system-maintenance,system-reboot,instance-stop,instance-reboot" --output text| grep -v Completed | awk -v acct="$account" '{print acct","$1","$2","$3","$NF}' > $TMP_FILE;
    ID=`cut -f 5 -d"," cat $TMP_FILE`;
    DATE=`cut -f 4 -d"," cat $TMP_FILE`;
    
    

    cd $HOME_PATH
done



