#!/usr/bin/python

"""This example shows how to work in adhoc mode

sta1 <---> sta2 <---> sta3"""

import sys

from mininet.log import setLogLevel, info
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.cli import CLI_wifi
from mn_wifi.net import Mininet_wifi
from mn_wifi.wmediumdConnector import interference


def topology(args):
    "Create a network."
    net = Mininet_wifi(link=wmediumd, wmediumd_mode=interference)

    info("*** Creating nodes\n")
    sta1 = net.addStation('sta1', position='10,10,0', range=100)
    sta2 = net.addStation('sta2', position='50,10,0', range=100)
    sta3 = net.addStation('sta3', position='90,10,0', range=100)
    sta4 = net.addStation('sta4', position='90,10,4', range=100)
    sta5 = net.addStation('sta5', position='90,10,5', range=100)

    net.setPropagationModel(model="logDistance", exp=4)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info("*** Creating links\n")

    net.addLink(sta1, cls=adhoc, intf='sta1-wlan0', ssid='adhocNet',
                mode='g', channel=5, ht_cap='HT40+')
    net.addLink(sta2, cls=adhoc, intf='sta2-wlan0', ssid='adhocNet',
                mode='g', channel=5)
    net.addLink(sta3, cls=adhoc, intf='sta3-wlan0', ssid='adhocNet',
                mode='g', channel=5, ht_cap='HT40+')
    net.addLink(sta4, cls=adhoc, intf='sta4-wlan0', ssid='adhocNet',
                mode='g', channel=5, ht_cap='HT40+')
    net.addLink(sta5, cls=adhoc, intf='sta5-wlan0', ssid='adhocNet',
                mode='g', channel=5, ht_cap='HT40+')

    info("*** Starting network\n")
    net.build()

#    info("\n*** Starting ROS2 nodes...\n")
#    sta1.cmd('ros2 run testbed_nodes testbed_robot r1 GS -v')
#    sta2.cmd('ros2 run testbed_nodes testbed_robot r2 red_team -v')

    info("*** Running CLI\n")
    CLI_wifi(net)

    info("*** Stopping network\n")
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    topology(sys.argv)
