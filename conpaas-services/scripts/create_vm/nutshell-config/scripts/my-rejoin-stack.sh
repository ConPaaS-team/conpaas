#! /usr/bin/env bash

# This script rejoins an existing screen, or re-creates a
# screen session from a previous run of stack.sh.

TOP_DIR=`dirname $0`
echo $TOP_DIR
# Import common functions in case the localrc (loaded via stackrc)
# uses them.
source $TOP_DIR/functions

source $TOP_DIR/stackrc

# if screenrc exists, run screen
if [[ -e $TOP_DIR/stack-screenrc ]]; then
    if screen -ls | egrep -q "[0-9].stack"; then
        echo "Screen session already started.."
        exit 0
    fi
  
    if [[ $EUID -eq 0 ]]; then
        exit 100
    fi

    VOLUME_GROUP="stack-volumes"
    BACKING_FILE="/opt/stack/data/stack-volumes-backing-file"
    DEV=`sudo losetup -f`
    
    if [[ -f $BACKING_FILE ]]; then

      if ! sudo losetup -a | grep $BACKING_FILE &> /dev/null ; then
          sudo losetup $DEV $BACKING_FILE
      fi

      if ! sudo vgs $VOLUME_GROUP  ; then
          DEV=`sudo losetup -a | grep $BACKING_FILE | cut -d':' -f1`
          sudo vgcreate $VOLUME_GROUP $DEV
      fi
    fi
 
    exec screen -d -m -c $TOP_DIR/stack-screenrc
fi

echo "Couldn't find $TOP_DIR/stack-screenrc file; have you run stack.sh yet?"
exit 1
