#!/bin/bash
# usage: minininet_runner.py <py file> <csv file> <output file>
echo Command: ./mininet_runner.py $1 $2 $3

sudo LD_LIBRARY_PATH="${LD_LIBRARY_PATH}" \
     AMENT_PREFIX_PATH="${AMENT_PREFIX_PATH}" \
     COLCON_PREFIX_PATH="${COLCON_PREFIX_PATH}" \
     PYTHONPATH="${PYTHONPATH}" \
     PATH="${PATH}" \
     ROS_SECURITY_ROOT_DIRECTORY="${ROS_SECURITY_ROOT_DIRECTORY}" \
     ROS_SECURITY_ENABLE="${ROS_SECURITY_ENABLE}" \
     ROS_SECURITY_STRATEGY="${ROS_SECURITY_STRATEGY}" \
     ./mininet_runner.py $1 $2 $3

