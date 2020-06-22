#!/usr/bin/python

import sys
from argparse import ArgumentParser
from os.path import join, expanduser, abspath
from importlib import import_module
from imp import load_source # Python2

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference

from setup_reader import read_setup, show_setup


#def start_runner(setup_file, out_file):
# returns network setup
def scenario_topology(setup):

    # get setup
    robots = setup["robots"]
    stations = setup["stations"]
    links = setup["links"]
    propagation_model = setup["propagation_model"]
    mobility_model = setup["mobility_model"]
    start_mobility = setup["start_mobility"]
    mobilities = setup["mobilities"]
    stop_mobility = setup["stop_mobility"]
    plot_graph = setup["plot_graph"]

    # log
    setLogLevel("info")

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    # station nodes
    info("mininet_runner: Creating station nodes\n")
    for robot_name, params in stations:
        print("addStation %s: %s"%(robot_name, params))
        net.addStation(robot_name, **params)

    if propagation_model:
        print("setPropagationModel: %s"%propagation_model)
        net.setPropagationModel(**propagation_model)

    info("mininet_runner: Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("mininet_runner: Creating links\n")
    for robot_name, params in links:
        print("addLink %s: %s"%(robot_name, params))
        net.addLink(net[robot_name], **params)

    # mobility
    if start_mobility:
        net.startMobility(**start_mobility)
    for robot_name, start_or_stop, params in mobilities:
        print("mobility %s: %s: %s"%(robot_name, start_or_stop, params))
        net.mobility(net[robot_name], start_or_stop, **params)
    if stop_mobility:
        net.stopMobility(**stop_mobility)

    if plot_graph != None: # do this evin if empty dict
        net.plotGraph(**plot_graph)

    if mobility_model:
        info("mininet_runner: Configuring mobility model\n")
        print("setMobilityModel: %s"%(mobility_model))
        net.setMobilityModel(**mobility_model)

    info("mininet_runner: Starting network\n")
    net.build()
    return net

# import file and run its topology(args) function, return net
def code_topology(code_filename):
    code_filename = abspath(expanduser(code_filename))
    print("Building network topology from %s"%code_filename)
    # https://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
    topology_module = load_source("myNetwork", code_filename)
    net = topology_module.myNetwork()
    return net

def start_robots(net, robots, setup_file, out_file):
    info("\nmininet_runner: Starting ROS2 nodes...\n")
    for robot in robots:
        robot_name = robot["robot_name"]
        role = robot["role"]
        logfile = "_log_%s"%robot_name
        cmd = "ros2 run testbed_nodes testbed_robot %s %s %s %s " \
              "> %s 2>&1 &"%(robot_name, role, setup_file, out_file, logfile)
        info("mininet_runner: Starting '%s'\n"%cmd)
        if not robot_name in net:
            print("Error with robot name '%s'"%robot_name)
        net[robot_name].cmd(cmd)

    # start Wireshark on first node object (first robot)
    net[robots[0]["robot_name"]].cmd("wireshark &")

    info("mininet_runner: Running CLI\n")
    CLI(net)

    info("mininet_runner: Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    # args
    parser = ArgumentParser(description="Start Mininet swarm emulation")
    parser.add_argument("setup_file", type=str, help="Testbed setup file")
    parser.add_argument("out_file", type=str, help="Output file")
    parser.add_argument("-s", "--script_setup", type=str,
                        help="Use network setup script from Python file")

    args = parser.parse_args()
    setup_file = expanduser(args.setup_file)
    out_file = expanduser(args.out_file)
    if args.script_setup:
        script_setup_filename = abspath(expanduser(args.script_setup))
    else:
        script_setup_filename = None

    # clear any existing content from out_file
    with open(out_file, "w") as f:
        f.flush()

    # read setup
    setup = read_setup(setup_file)
    show_setup(setup_file, setup)

    # show total count of robot nodes
    print("Robot count: %d"%len(setup["robots"]))

    # configuration approach
    if args.script_setup:
        net = code_topology(args.script_setup)

    else:
        # use the scenario topology
        net = scenario_topology(setup)

    # start the robots
    start_robots(net, setup["robots"], setup_file, out_file)

