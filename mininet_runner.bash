#!/bin/bash
# usage: minininet_runner.py <py file> <csv file> <output file>
echo Command: ./mininet_runner.py $1 $2 $3

sudo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
     "AMENT_PREFIX_PATH=${AMENT_PREFIX_PATH}" \
     "COLCON_PREFIX_PATH=${COLCON_PREFIX_PATH}" \
     "PYTHONPATH=${PYTHONPATH}" \
     "PATH=${PATH}" \
     ./mininet_runner.py $1 $2 $3

