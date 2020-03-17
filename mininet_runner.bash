#!/bin/bash
# usage: minininet_runner.py <setup file> <output file>
sudo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
     "AMENT_PREFIX_PATH=${AMENT_PREFIX_PATH}" \
     "COLCON_PREFIX_PATH=${COLCON_PREFIX_PATH}" \
     "PYTHONPATH=${PYTHONPATH}" \
     "PATH=${PATH}" \
     ./mininet_runner.py $1 $2

