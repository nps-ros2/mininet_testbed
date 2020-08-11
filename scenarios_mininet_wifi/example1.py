#!/usr/bin/python

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.wmediumdConnector import interference
from subprocess import call


def myNetwork():

    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches/APs\n')

    info( '*** Add hosts/stations\n')
    R1 = net.addStation('R1', ip='10.0.0.1', position='0.0,0.0,0')
    R2 = net.addStation('R2', ip='10.0.0.2', position='1.0,0.0,0')
    R3 = net.addStation('R3', ip='10.0.0.3', position='0.0,1.0,0')
    R4 = net.addStation('R4', ip='10.0.0.4', position='-1.0,0.0,0')
    R5 = net.addStation('R5', ip='10.0.0.5', position='0.0,-1.0,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(R1, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R1-wlan0')
    net.addLink(R2, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R2-wlan0')
    net.addLink(R3, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R3-wlan0')
    net.addLink(R4, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R4-wlan0')
    net.addLink(R5, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R5-wlan0')

    net.plotGraph(min_x=-2, min_y=-2, max_x=2, max_y=2)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')

    info( '*** Post configure nodes\n')

#    CLI(net)
#    net.stop()

    return net


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

