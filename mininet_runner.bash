#!/bin/bash
# usage: minininet_runner.py <setup file> <output file> [-t "<option ...>"]
echo Command: ./mininet_runner.py $1 $2 $3 "$4"

if [[ -z $3 && -z $4 ]]; then

    sudo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
         "AMENT_PREFIX_PATH=${AMENT_PREFIX_PATH}" \
         "COLCON_PREFIX_PATH=${COLCON_PREFIX_PATH}" \
         "PYTHONPATH=${PYTHONPATH}" \
         "PATH=${PATH}" \
         ./mininet_runner.py $1 $2

else

    sudo "LD_LIBRARY_PATH=${LD_LIBRARY_PATH}" \
         "AMENT_PREFIX_PATH=${AMENT_PREFIX_PATH}" \
         "COLCON_PREFIX_PATH=${COLCON_PREFIX_PATH}" \
         "PYTHONPATH=${PYTHONPATH}" \
         "PATH=${PATH}" \
         ./mininet_runner.py $1 $2 $3 "$4"

fi

