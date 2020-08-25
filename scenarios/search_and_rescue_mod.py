#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call

def myNetwork():

    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch, failMode='standalone')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)

    info( '*** Add links\n')
    # example QoS
    satellite_qos = {'bw':1000,'delay':'400ms','loss':1,
                     'max_queue_size':10,'jitter':'50ms'}
    home_wifi_qos = {'bw':100,'delay':'2ms','loss':1,
                     'max_queue_size':10,'jitter':'1ms'}
    trailer_wifi_qos = {'bw':100,'delay':'2ms','loss':1,
                     'max_queue_size':10,'jitter':'1ms'}
    drone_wifi_qos = {'bw':100,'delay':'3ms','loss':1,
                     'max_queue_size':10,'jitter':'1ms'}

    net.addLink(h1, s1, cls=TCLink , **home_wifi_qos)
    net.addLink(s1, s2, cls=TCLink , **satellite_qos)
    net.addLink(s2, h2, cls=TCLink , **satellite_qos)
    net.addLink(s2, s3, cls=TCLink , **satellite_qos)
    net.addLink(s3, s4, cls=TCLink , **trailer_wifi_qos)
    net.addLink(s4, h3, cls=TCLink , **drone_wifi_qos)
    net.addLink(s4, h4, cls=TCLink , **drone_wifi_qos)
    net.addLink(s4, h5, cls=TCLink) # direct link

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([])
    net.get('s2').start([])
    net.get('s3').start([])
    net.get('s4').start([])

    info( '*** Post configure switches and hosts\n')

#    CLI(net)
#    net.stop()
    return net

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

