#!/bin/bash

CPS_LIB="../conpaas-services/src"
CPS_TOOLS="./src"

export PYTHONPATH="$CPS_TOOLS:$CPS_LIB"
python -m cps_tools.cps_tools $*

