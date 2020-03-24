#!/bin/bash
# usage: minininet_runner.py <setup file> <output file>
if [[ -z $1 && -z $2 ]]; then
    SETUP_FILE="~/gits/mininet_testbed/scenarios/example1.csv"
    OUTPUT_FILE="_mininet_test_outfile"
    echo Using hardcoded paths ${SETUP_FILE} and ${OUTPUT_FILE}
else
    SETUP_FILE=$1
    OUTPUT_FILE=$2
fi

sudo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
     "AMENT_PREFIX_PATH=${AMENT_PREFIX_PATH}" \
     "COLCON_PREFIX_PATH=${COLCON_PREFIX_PATH}" \
     "PYTHONPATH=${PYTHONPATH}" \
     "PATH=${PATH}" \
     ./mininet_runner.py ${SETUP_FILE} ${OUTPUT_FILE}

