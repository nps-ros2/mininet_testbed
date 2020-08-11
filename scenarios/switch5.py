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
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')
    s4 = net.addSwitch('s4', cls=OVSKernelSwitch, failMode='standalone')
    s5 = net.addSwitch('s5', cls=OVSKernelSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')

    info( '*** Add hosts\n')
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h5 = net.addHost('h5', cls=Host, ip='10.0.0.5', defaultRoute=None)

    info( '*** Add links\n')
    s1s2 = {'delay':'200ms'}
    net.addLink(s1, s2, cls=TCLink , **s1s2)
    s2s3 = {'delay':'200ms'}
    net.addLink(s2, s3, cls=TCLink , **s2s3)
    s3s4 = {'delay':'200ms'}
    net.addLink(s3, s4, cls=TCLink , **s3s4)
    s4s5 = {'delay':'200ms'}
    net.addLink(s4, s5, cls=TCLink , **s4s5)
    s1h1 = {'delay':'100ms'}
    net.addLink(s1, h1, cls=TCLink , **s1h1)
    s2h2 = {'delay':'100ms'}
    net.addLink(s2, h2, cls=TCLink , **s2h2)
    s3h3 = {'delay':'100ms'}
    net.addLink(s3, h3, cls=TCLink , **s3h3)
    s4h4 = {'delay':'100ms'}
    net.addLink(s4, h4, cls=TCLink , **s4h4)
    s5h5 = {'delay':'100ms'}
    net.addLink(s5, h5, cls=TCLink , **s5h5)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([])
    net.get('s3').start([])
    net.get('s4').start([])
    net.get('s5').start([])
    net.get('s2').start([])

    info( '*** Post configure switches and hosts\n')

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

