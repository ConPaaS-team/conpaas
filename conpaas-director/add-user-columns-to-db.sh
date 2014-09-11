#!/bin/bash

temp=`mktemp --tmpdir=. -t cpsdir-XXXXXXX`
uuid_present=false
if [ $# -eq 0 ]
then
    ORIG_DB=/etc/cpsdirector/director.db
else
    ORIG_DB=$1
fi
echo check $ORIG_DB
echo .dump | sqlite3 $ORIG_DB > $temp.dump
LS="`ls -l  $ORIG_DB`"

updated=false
for user_field in uuid openid
do
        # echo Check presence of field $user_field
        field_present=false
        grep $user_field $temp.dump > /dev/null && field_present=true
        # echo $field_present
        if $field_present
        then
                echo Field $user_field already present
        else
                case $user_field in
                uuid) LEN=80;;
                openid) LEN=200;;
                esac
                echo Adding field $user_field to DB
                # 1) add column 'user_field' as last column in "user" table, just in front of the PRIMARY key
                # 2) add empty 'user_field' values to existing users
    sed -i '
        /PRIMARY KEY (uid)/i \
        '$user_field' VARCHAR('$LEN'),
        /INTO "user" VALUES/s/);$/,'"''"'&/ 
    ' $temp.dump
                sqlite3 $temp.new-director.db < $temp.dump
                echo .dump | sqlite3 $temp.new-director.db > $temp.new-director.dump
                # less $temp.dump
                # less $temp.new-director.dump
                diff_ok=false
                diff $temp.dump $temp.new-director.dump && diff_ok=true
                if `$diff_ok`
                then
                        mv $temp.new-director.db $ORIG_DB
                        echo Update completed
                        updated=true
                else
                        echo Something was wrong, DB not replaced
                        exit 1
                fi
        fi
done
if $updated
then
echo "You may need to change ownership of the database
original
        $LS
now
        `ls -l  $ORIG_DB`
"
fi
rm $temp*
exit
