#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import *
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import Link, TCLink

def topology():
    net = Mininet(controller = RemoteController, link = TCLink, switch = OVSKernelSwitch)
    print("*** Twozenie wezlow")
    s1 = net.addSwitch('s1', protocols = 'OpenFlow13', mac = '00:00:00:00:00:01')
    s2 = net.addSwitch('s2', protocols = 'OpenFlow13', mac = '00:00:00:00:00:02')
    s3 = net.addSwitch('s3', protocols = 'OpenFlow13', mac = '00:00:00:00:00:03')
    s4 = net.addSwitch('s4', protocols = 'OpenFlow13', mac = '00:00:00:00:00:04')
    s5 = net.addSwitch('s5', protocols = 'OpenFlow13', mac = '00:00:00:00:00:05')
    s6 = net.addSwitch('s6', protocols = 'OpenFlow13', mac = '00:00:00:00:00:06')
    s7 = net.addSwitch('s7', protocols = 'OpenFlow13', mac = '00:00:00:00:00:07')
    c1 = net.addController('c1',controller = RemoteController, ip = '192.168.174.129', port = 6653)
    h1 = net.addHost('h1')
    h2 = net.addHost('h2')
    print("*** Twozenie polaczen")
    net.addLink(s1,s2)
    net.addLink(s1,s3)
    net.addLink(s2,s4)
    net.addLink(s2,s6)
    net.addLink(s2,s3)
    net.addLink(s3,s6)
    net.addLink(s4,s5)
    net.addLink(s5,s7)
    net.addLink(s5,s6)
    net.addLink(s6,s7)
    net.addLink(h1,s1)
    net.addLink(h2,s7)
    print('*** Start sieci')
    net.build()
    c1.start()
    s1.start([c1])
    s2.start([c1])
    s3.start([c1])
    s4.start([c1])
    s5.start([c1])
    s6.start([c1])
    s7.start([c1])
    print('*** Wlaczanie statycznego ARP')
    net.staticArp()
    print("*** Start CLI")
    CLI( net )
    print("*** Stop sieci")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    topology()
