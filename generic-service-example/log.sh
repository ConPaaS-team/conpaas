#!/bin/bash

LOG=0

# date
# echo LOG=$LOG
function crashed {
        echo CRASHED with exit value $? | tee -a /dev/stderr 
        exit 1 
}
function log {
        LOG=`expr $LOG + 1`
        # echo logging stdout $LOG
    if false
    then
        echo '$#' = $#
        ii=0
        
        FUNCARGV=($@)
        for i in "$@"
        do
                ii=`expr $ii + 1`
                echo '$'"$ii" = $i
        done
        echo REST = $@
    fi

        case $1 in
                -*)
                        option=$1 ; shift
                        echo option = $option
                        case $option in
                        -d)     echo '==>' `date` : $@ | tee -a /dev/stderr
                        ;;
                        -s)     echo '==>' `date` : $@ '(SKIPPED)' | tee -a /dev/stderr
                        ;;
                        -C)     echo '==>' `date` : $@ | tee -a /dev/stderr
                                $@
                        ;;
                        -c)     echo '==>' `date` : $@ | tee -a /dev/stderr
                                $@ || crashed
                        ;;
                        -T)     echo '==>' `date` : $@ | tee -a /dev/stderr
                                time $@
                        ;;
                        -t)     echo '==>' `date` : $@ | tee -a /dev/stderr
                                time $@ || crashed
                        ;;
                        *)      echo "Unknown option '$option'"
                        ;;
                        esac
                ;;
                *)
                        sleep 1
                        date
                        LOG=`expr $LOG + 1`
                        echo logging stdout $LOG
                        echo '$#' = $#
                        ii=0
                        for i in "$@"
                        do
                                ii=`expr $ii + 1`
                                echo '$'"$ii" = $i
                        done
                        sleep 1
                        LOG=`expr $LOG + 1`
                        date >>/dev/stderr
                        echo logging stderr $LOG >>/dev/stderr
                        exit 1
                ;;
        esac
}
