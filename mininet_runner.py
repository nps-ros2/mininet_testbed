#!/usr/bin/python

import sys
from argparse import ArgumentParser

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference

from setup_reader import read_setup


def start_runner(setup_file, out_file):

    # clear any existing content from out_file
    with open(out_file, "w") as f:
        f.flush()

    # get total count of Wifi devices
    _publishers, _subscribers, mobilities = read_setup(infile)

    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    stations = list()
    for i, mobility in enumerate(mobilities):
        station_name = "sta%d"%i # sta0
        position = [mobility.position_string]
        station_range = 100
        station = net.addStation(station_name, position=position,
                                 range=station_range)
        stations.append(station)

    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")

    for i in range(len(mobilities)):
        station = stations[i]
        net.addLink(station, cls=adhoc, intf='sta1-wlan0', ssid='adhocNet',
                    mode='g', channel=5, ht_cap='HT40+')

    info("*** Starting network\n")
    net.build()

    info("\n*** Starting ROS2 nodes...\n")
    for i, mobility in enumerate(mobilities):
        station = stations[i]
        robot_name = "r%d"%i
        role = mobility.role
        station.cmd("ros2 run testbed_nodes testbed_robot %s %s %s %s &")%(
                                robot_name, role, setup_file, out_file)

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    default_setup_file = join(expanduser("~"),
                         "gits/mininet_testbed/testbed/csv_roles/example1.csv")
    default_out_file = "_mininet_runner_out"
    # args
    parser = ArgumentParser(description="Start Mininet swarm emulation")
    parser.add_argument("-s","--setup_file", type=str,
                        help="Testbed setup file", default=default_setup_file)
    parser.add_argument("-o", "--out_file", type=str,
                        help="Output file", default=default_out_file)
    args = parser.parse_args()

    start_runner(args.setup_file, args.out_file)

