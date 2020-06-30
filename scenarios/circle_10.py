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
    R01 = net.addStation('R01', ip='10.0.0.1', position='2.0,1.0,0')
    R02 = net.addStation('R02', ip='10.0.0.2', position='3.0,1.0,0')
    R03 = net.addStation('R03', ip='10.0.0.3', position='4.0,1.0,0')
    R04 = net.addStation('R04', ip='10.0.0.4', position='5.0,2.0,0')
    R05 = net.addStation('R05', ip='10.0.0.5', position='5.0,3.0,0')
    R06 = net.addStation('R06', ip='10.0.0.6', position='4.0,4.0,0')
    R07 = net.addStation('R07', ip='10.0.0.7', position='3.0,4.0,0')
    R08 = net.addStation('R08', ip='10.0.0.8', position='2.0,4.0,0')
    R09 = net.addStation('R09', ip='10.0.0.9', position='1.0,3.0,0')
    R10 = net.addStation('R10', ip='10.0.0.10', position='1.0,2.0,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(R01, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R01-wlan0')
    net.addLink(R02, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R02-wlan0')
    net.addLink(R03, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R03-wlan0')
    net.addLink(R04, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R04-wlan0')
    net.addLink(R05, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R05-wlan0')
    net.addLink(R06, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R06-wlan0')
    net.addLink(R07, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R07-wlan0')
    net.addLink(R08, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R08-wlan0')
    net.addLink(R09, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R09-wlan0')
    net.addLink(R10, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='R10-wlan0')

    net.plotGraph(min_x=0, min_y=0, max_x=6, max_y=5)

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

