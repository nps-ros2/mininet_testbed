#!/usr/bin/python

import sys
from argparse import ArgumentParser
from os.path import join, expanduser

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference

from setup_reader import read_setup, show_setup


def start_runner(setup_file, out_file):

    # clear any existing content from out_file
    with open(out_file, "w") as f:
        f.flush()

    # get setup
    setup = read_setup(setup_file)
    show_setup(setup_file, setup)
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

    # get total count of robot nodes
    print("Robot count: %d"%len(robots))

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    # instantiated stations
    station_objects = dict()

    # station nodes
    info("mininet_runner: Creating station nodes\n")
    for robot_name, params in stations:
        print("addStation %s: %s"%(robot_name, params))
        station_objects[robot_name] = net.addStation(robot_name, **params)

    if propagation_model:
#        info("mininet_runner: Configuring propagation model\n")
        print("setPropagationModel: %s"%propagation_model)
        net.setPropagationModel(**propagation_model)

    info("mininet_runner: Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("mininet_runner: Creating links\n")
    for robot_name, params in links:
        print("addLink %s: %s"%(robot_name, params))
        net.addLink(station_objects[robot_name], **params)

    # mobility
    if start_mobility:
        net.startMobility(**start_mobility)
    for robot_name, start_or_stop, params in mobilities:
        print("mobility %s: %s: %s"%(robot_name, start_or_stop, params))
        net.mobility(station_objects[robot_name], start_or_stop, **params)
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

    info("\nmininet_runner: Starting ROS2 nodes...\n")
    for robot in robots:
        robot_name = robot["robot_name"]
        station_object = station_objects[robot_name]
        role = robot["role"]
        logfile = "_log_%s"%robot_name
        cmd = "ros2 run testbed_nodes testbed_robot %s %s %s %s " \
              "> %s 2>&1 &"%(robot_name, role, setup_file, out_file, logfile)
        info("mininet_runner: Starting '%s'\n"%cmd)
        station_object.cmd(cmd)
#        info("mininet_runner: Not Starting '%s'\n"%cmd)

    # start Wireshark on first node object (first robot)
    station_objects[robots[0]["robot_name"]].cmd("wireshark &")

    info("mininet_runner: Running CLI\n")
    CLI_wifi(net)

    info("mininet_runner: Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    # args
    parser = ArgumentParser(description="Start Mininet swarm emulation")
    parser.add_argument("setup_file", type=str, help="Testbed setup file")
    parser.add_argument("out_file", type=str, help="Output file")
    args = parser.parse_args()

    start_runner(expanduser(args.setup_file), expanduser(args.out_file))

