#!/usr/bin/python

import sys
from argparse import ArgumentParser
from os.path import join, expanduser, abspath
from importlib import import_module
from imp import load_source # Python2
from mininet.log import info
from mininet.cli import CLI

from setup_reader import read_setup, show_setup

# import file and run its topology(args) function, return net
def code_topology(py_file):
    print("Building network topology from %s"%py_file)
    # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    topology_module = load_source("myNetwork", py_file)
    net = topology_module.myNetwork()
    return net

def start_robots(net, robots, csv_file, out_file):
    info("\nmininet_runner: Starting ROS2 nodes...\n")
    for robot in robots:
        robot_name = robot["robot_name"]
        role = robot["role"]
        logfile = "_log_%s"%robot_name
        cmd = "ros2 run testbed_nodes testbed_robot %s %s %s %s " \
              "> %s 2>&1 &"%(robot_name, role, csv_file, out_file, logfile)
        info("mininet_runner: Starting '%s'\n"%cmd)
        if not robot_name in net:
            print("Error with robot name '%s'"%robot_name)
        net[robot_name].cmd(cmd)

#    # start Wireshark on first node object (first robot)
#    net[robots[0]["robot_name"]].cmd("wireshark &")

if __name__ == '__main__':
    # args
    parser = ArgumentParser(description="Start Mininet swarm emulation")
    parser.add_argument("py_file", type=str, help="Python network setup file")
    parser.add_argument("csv_file", type=str,
                        help="CSV communication setup file")
    parser.add_argument("out_file", type=str, help="Log output file")

    args = parser.parse_args()
    csv_file = expanduser(args.csv_file)
    py_file = abspath(expanduser(args.py_file))
    out_file = expanduser(args.out_file)

    # clear any existing content from out_file
    with open(out_file, "w") as f:
        f.flush()

    # read setup
    setup = read_setup(csv_file)
    show_setup(csv_file, setup)

    # show total count of robot nodes
    print("Robot count: %d"%len(setup["robots"]))

    # load the network topology from myNetwork created by miniedit
    print("Building network topology from %s"%py_file)
    topology_module = load_source("myNetwork", py_file)
    net = topology_module.myNetwork()

    # avoid any setup delay by performing an all-pairs ping
    net.pingAll()

    # start the robots
    start_robots(net, setup["robots"], csv_file, out_file)

    # start CLI
    info("mininet_runner: Running CLI\n")
    CLI(net)

    # on exit or Ctrl-D
    info("mininet_runner: Stopping network\n")
    net.stop()

