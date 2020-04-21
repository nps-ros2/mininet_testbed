#!/usr/bin/python

import sys
from argparse import ArgumentParser
from os.path import join, expanduser

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference

from read_robots import read_robots


def start_runner(setup_file, out_file):

    # clear any existing content from out_file
    with open(out_file, "w") as f:
        f.flush()

    # get total count of Wifi devices
    robots = read_robots(setup_file)
    print("Robot count: %d"%len(robots))

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    stations = dict()
    for robot in robots:
        station_name = robot.robot_name
        position = robot.position_string()
        station_range = 100
        info(" station %s position %s range %d\n"%(
                                  station_name, position, station_range))
        station = net.addStation(station_name, position=position,
                                 range=station_range)
        stations[robot] = station

    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")

    for robot in robots:
        station = stations[robot]
        net.addLink(station, cls=adhoc, intf='%s-wlan0'%robot.robot_name,
                    ssid='adhocNet', mode='g', channel=5, ht_cap='HT40+')

    info("*** Starting network\n")
    net.build()

    info("\n*** Starting ROS2 nodes...\n")
    for robot in robots:
        station = stations[robot]
        robot_name = robot.robot_name
        role = robot.role
        logfile = "_log_%s"%robot_name
        cmd = "ros2 run testbed_nodes testbed_robot %s %s %s %s " \
              "> %s 2>&1 &"%(robot_name, role, setup_file, out_file, logfile)
        info("*** Starting '%s'\n"%cmd)
        station.cmd(cmd)
#        info("*** Not Starting '%s'\n"%cmd)

    # start Wireshark on first station (first robot)
    stations[robots[0]].cmd("wireshark &")

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

