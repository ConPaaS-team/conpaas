#!/bin/bash
rm -f log.err log.out

./logtest-1.sh >> log.out 2>>log.err

tail -n 50 log.???
