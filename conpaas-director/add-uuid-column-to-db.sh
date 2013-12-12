#!/bin/bash


temp=`mktemp --tmpdir=. -t cpsdir-XXXXXXX`
uuid_present=false
ORIG_DB=/etc/cpsdirector/director.db
echo .dump | sqlite3 $ORIG_DB > $temp.dump
grep uuid $temp.dump > /dev/null && uuid_present=true

if `$uuid_present`
then
    echo DB already updated
else
    echo Updating DB
    # 1) add column uuid as last column in "user" table, just in front of the PRIMARY key
    # 2) add empty uuid values to existing users
    sed -i '
        /PRIMARY KEY (uid)/i \
        uuid VARCHAR(80),
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
        else
                echo Something was wrong, DB not replaced
                exit 1
        fi
fi
rm $temp*
exit
