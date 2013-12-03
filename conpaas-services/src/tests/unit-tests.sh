#!/bin/bash

UNIT_TEST_LOG_DIR="./unit-tests-logs"
MODULES="../conpaas/services/webservers"

export PYTHONPATH=".."

PEP8_OPTIONS=""
# disable line length checks (default 80 characters is harsh)
PEP8_OPTIONS="$PEP8_OPTIONS --ignore=E501"

PYLINT_FATAL=1
PYLINT_ERROR=2
PYLINT_WARNING=4
PYLINT_REFACTOR=8
PYLINT_CONVENTION=16
PYLINT_USAGE=32

PYLINT_FILTER=$(($PYLINT_FATAL | $PYLINT_ERROR))

PYLINT_OPTIONS=""
# extend maximum line length from 80 to 100 characters
PYLINT_OPTIONS="$PYLINT_OPTIONS --max-line-length=100"
# disable errors when pylint is not sure about the type ie errors like "(but some types could not be inferred)"
PYLINT_OPTIONS="$PYLINT_OPTIONS --disable=E1103"
# disable warnings about missing comments
PYLINT_OPTIONS="$PYLINT_OPTIONS --disable=C"
# disable warnings about recommendations (like number of parameters, number of methods, etc.)
PYLINT_OPTIONS="$PYLINT_OPTIONS --disable=R"

#
# Syntax and basic checks with pep8 and pylint
#

mkdir -p "$UNIT_TEST_LOG_DIR"

for mod in $MODULES
do
    pyfiles="$(find $mod -name '*.py' \! -empty)"

    for pyfile in $pyfiles
    do
      echo "File $pyfile : "

      echo -n "  PEP8"
      pep8 $PEP8_OPTIONS $pyfile
      if [ $? -ne 0 ]
      then
        exit 1
      fi
      echo " OK"

      echo -n "  PYLINT"
      pyfile_base="${pyfile//\//.}"
      pyfile_base="$(echo $pyfile_base | sed 's/^[\.]*//')"
      pylint_log="$UNIT_TEST_LOG_DIR/${pyfile_base%.py}-pylint.log"
      pylint $PYLINT_OPTIONS $pyfile > $pylint_log 2>&1
      if [ $(($? & $PYLINT_FILTER)) -ne 0 ]
      then
        cat $pylint_log
        exit 1
      fi
      echo " OK"
      grep "Your code has been rated at" $pylint_log | sed 's/.*rated at/   /'
    done
done


#
# pyunit tests with code coverage statistics
#
export PYTHONPATH=..
COVERAGE="`which python-coverage || true`"
if [ -z "$COVERAGE" ]
then
    COVERAGE="`which coverage`"
fi

$COVERAGE run --source=conpaas run_tests.py
$COVERAGE report -m

