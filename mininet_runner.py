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
    log_level = setup["log_level"]
    plot_graph = setup["plot_graph"]

    # log
    if log_level:
        setLogLevel(log_level)

    # get total count of Wifi devices
    print("Robot count: %d"%len(robots))

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    station_objects = dict()
    for robot in robots:
        robot_name = robot["robot_name"]
        print("addStation %s: %s"%(robot_name, (stations[robot_name])))
        station_objects[robot_name] = net.addStation(robot_name,
                                                    **stations[robot_name])

    net.setPropagationModel(**propagation_model)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")
    for robot in robots:
        robot_name = robot["robot_name"]
        station = station_objects[robot_name]
        params = links[robot_name]
        params["cls"] = adhoc
        params["intf"] = '%s-wlan0'%robot_name
        print("station: ", station)
        print("params: ", params)

        print("addLink%s: %s"%(station, params))
        net.addLink(station, **params)

    net.plotGraph(**plot_graph)

    info("*** Configuring mobility model\n")
    net.setMobilityModel(**mobility_model)


    info("*** Starting network\n")
    net.build()

    info("\n*** Starting ROS2 nodes...\n")
    for robot in robots:
        robot_name = robot["robot_name"]
        station = station_objects[robot_name]
        role = robot["role"]
        logfile = "_log_%s"%robot_name
        cmd = "ros2 run testbed_nodes testbed_robot %s %s %s %s " \
              "> %s 2>&1 &"%(robot_name, role, setup_file, out_file, logfile)
        info("*** Starting '%s'\n"%cmd)
        station.cmd(cmd)
#        info("*** Not Starting '%s'\n"%cmd)

    # start Wireshark on first station (first robot)
    station_objects[robots[0]["robot_name"]].cmd("wireshark &")

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')

    # args
    parser = ArgumentParser(description="Start Mininet swarm emulation")
    parser.add_argument("setup_file", type=str, help="Testbed setup file")
    parser.add_argument("out_file", type=str, help="Output file")
    args = parser.parse_args()

    start_runner(expanduser(args.setup_file), expanduser(args.out_file))

