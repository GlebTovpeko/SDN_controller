#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QoS Topology - WORKING VERSION WITH REMOTE CONTROLLER"""
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time
import os
class QoSTopology(Topo):
    def build(self):
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        
        s1 = self.addSwitch('s1', protocols='OpenFlow13', dpid='0000000000000001')
        s2 = self.addSwitch('s2', protocols='OpenFlow13', dpid='0000000000000002')
        s3 = self.addSwitch('s3', protocols='OpenFlow13', dpid='0000000000000003')
        
        self.addLink(s1, s2, bw=100, delay='1ms', use_htb=True)
        self.addLink(s1, s3, bw=10, delay='50ms', use_htb=True)
        self.addLink(s3, s2, bw=10, delay='50ms', use_htb=True)
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
def run():
    onos_host = os.environ.get('ONOS_HOST', '172.28.0.2')
    onos_port = int(os.environ.get('ONOS_PORT', '6653'))
    
    topo = QoSTopology()
    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=RemoteController('onos', ip=onos_host, port=onos_port),
        switch=OVSKernelSwitch,
        autoSetMacs=True,
        autoStaticArp=True,    # ✅ Статический ARP для мгновенного разрешения
        waitConnected=False
    )
    
    info("*** Starting QoS Network\n")
    net.start()
    
    info("*** Waiting 45s for switches to connect to ONOS...\n")
    time.sleep(45)
    
    info("*** Adding static ARP entries...\n")
    for host in net.hosts:
        for other in net.hosts:
            if host != other:
                host.setARP(other.IP(), other.MAC())
    
    info("*** Testing connectivity...\n")
    net.pingAll()  # ✅ Простой вызов без обработки результата
    
    info("\n" + "="*60)
    info(" CLI READY - Test commands:\n")
    info("   pingall          # All-to-all connectivity\n")
    info("   h3 ping 10.0.0.4 # VoIP path (~1ms via s1-s2)\n")
    info("   h1 ping 10.0.0.2 # Regular path (~50ms via s1-s3-s2)\n")
    info("   net              # Show topology\n")
    info("="*60 + "\n\n")
    
    CLI(net)
    net.stop()
if __name__ == '__main__':
    setLogLevel('info')
    run()
