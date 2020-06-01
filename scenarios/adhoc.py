#!/usr/bin/python

from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI_wifi
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
    sta1 = net.addStation('sta1', ip='10.0.0.1',
                           position='3.0,2.0,0')
    sta3 = net.addStation('sta3', ip='10.0.0.3',
                           position='5.0,4.0,0')
    sta2 = net.addStation('sta2', ip='10.0.0.2',
                           position='8.0,9.0,0')

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(sta1, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='sta1-wlan0')
    net.addLink(sta3, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='sta3-wlan0')
    net.addLink(sta3, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='sta3-wlan0')
    net.addLink(sta2, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='sta2-wlan0')
    net.addLink(sta1, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='sta1-wlan0')
    net.addLink(sta2, cls=adhoc, ssid='new-ssid', mode='g', channel=1, intf='sta2-wlan0')

    net.plotGraph(max_x=1000, max_y=1000)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')

    info( '*** Post configure nodes\n')

#    CLI_wifi(net)
#    net.stop()

    return net

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

