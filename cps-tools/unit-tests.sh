#!/bin/bash

PYFILE_ROOT="."
SOURCE="./src"
TEST_SOURCE="./test"
CPS_LIB="../conpaas-services/src"
CPS_DIRECTOR="../conpaas-director"

UNIT_TEST_LOG_DIR="./unit-test-logs"

PYLINT_FATAL=1
PYLINT_ERROR=2
PYLINT_WARNING=4
PYLINT_REFACTOR=8
PYLINT_CONVENTION=16
PYLINT_USAGE=32

PYLINT_FILTER=$(($PYLINT_FATAL | $PYLINT_ERROR))


export PYTHONPATH="$SOURCE:$TEST_SOURCE:$CPS_LIB:$CPS_DIRECTOR"


#
# Syntax and basic checks with pep8 and pylint
#

mkdir -p "$UNIT_TEST_LOG_DIR"

pyfiles="$(find $PYFILE_ROOT -name '*.py' \! -empty)"

for pyfile in $pyfiles
do
  echo "File $pyfile : "

  echo -n "  PEP8"
  pep8 --ignore=E501 $pyfile
  if [ $? -ne 0 ]
  then
    exit 1
  fi
  echo " OK"
  
  echo -n "  PYLINT"
  pyfile_base="$(basename $pyfile)"
  pylint_log="$UNIT_TEST_LOG_DIR/${pyfile_base%.py}-pylint.log"
  pylint --max-line-length=100 $pyfile > $pylint_log 2>&1
  if [ $(($? & $PYLINT_FILTER)) -ne 0 ]
  then
    cat $pylint_log
    exit 1
  fi
  echo " OK"
  grep "Your code has been rated at" $pylint_log | sed 's/.*rated at/   /'
done


#
#  Basic checking whether the parser is correctly configured
#
echo -n "Get help"
./cps-tools.sh -h > /dev/null
if [ $? -ne 0 ]
then
  exit 1
fi
echo " OK"


#
# Other unit tests
#
echo -n "Other unit tests"
python ./test/test_suite.py
if [ $? -ne 0 ]
then
  exit 1
fi
echo " OK"


