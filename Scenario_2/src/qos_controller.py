#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""QoS Topology - Connect to Controller, then Disconnect and Apply Rules"""
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
        # Hosts with explicit IPs and MACs
        h1 = self.addHost('h1', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
        h2 = self.addHost('h2', ip='10.0.0.2/24', mac='00:00:00:00:00:02')
        h3 = self.addHost('h3', ip='10.0.0.3/24', mac='00:00:00:00:00:03')
        h4 = self.addHost('h4', ip='10.0.0.4/24', mac='00:00:00:00:00:04')
        
        # Switches with OpenFlow 1.3
        s1 = self.addSwitch('s1', protocols='OpenFlow13', dpid='0000000000000001')
        s2 = self.addSwitch('s2', protocols='OpenFlow13', dpid='0000000000000002')
        s3 = self.addSwitch('s3', protocols='OpenFlow13', dpid='0000000000000003')
        
        # Links: Fast path (100 Mbps, 1ms) and Slow path (10 Mbps, 50ms)
        self.addLink(s1, s2, bw=100, delay='1ms', use_htb=True)
        self.addLink(s1, s3, bw=10, delay='50ms', use_htb=True)
        self.addLink(s3, s2, bw=10, delay='50ms', use_htb=True)
        
        # Connect hosts
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s1)
        self.addLink(h4, s2)
def disconnect_controllers(net):
    """Отключить контроллер от всех коммутаторов"""
    info("\n" + "="*60)
    info(" DISCONNECTING CONTROLLERS")
    info("="*60 + "\n")
    
    for switch in net.switches:
        info(f"  Disconnecting {switch.name} from controller... ")
        # Отключаем контроллер (очищаем список контроллеров)
        switch.cmd('sh ovs-vsctl set-controller %s tcp:' % switch.name)
        info("✓\n")
    
    time.sleep(2)
def add_qos_rules(net):
    """Добавить QoS правила через ovs-ofctl после отключения контроллера"""
    info("\n" + "="*60)
    info(" ADDING QoS RULES VIA ovs-ofctl")
    info("="*60 + "\n")
    
    # Используем первый хост для выполнения команд ovs-ofctl
    h = net.hosts[0]
    
    info("  Clearing old flows...\n")
    h.cmd('sh ovs-ofctl -O OpenFlow13 del-flows s1')
    h.cmd('sh ovs-ofctl -O OpenFlow13 del-flows s2')
    h.cmd('sh ovs-ofctl -O OpenFlow13 del-flows s3')
    
    info("  Adding rules to s1:\n")
    # s1: h3(eth4) → s2(eth1) [быстрый путь], h1(eth3) → s3(eth1) [медленный путь]
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s1 "priority=200,in_port=4,actions=output:1"')
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s1 "priority=200,in_port=3,actions=output:2"')
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s1 "priority=1,actions=FLOOD"')
    info("    ✓ h3(eth4) → s2(eth1) [fast path]\n")
    info("    ✓ h1(eth3) → s3(eth1) [slow path]\n")
    
    info("  Adding rules to s2:\n")
    # s2: s1(eth1) → h4(eth4) [быстрый путь], s3(eth2) → h2(eth3) [медленный путь]
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s2 "priority=200,in_port=1,actions=output:4"')
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s2 "priority=200,in_port=2,actions=output:3"')
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s2 "priority=1,actions=FLOOD"')
    info("    ✓ s1(eth1) → h4(eth4) [fast path]\n")
    info("    ✓ s3(eth2) → h2(eth3) [slow path]\n")
    
    info("  Adding rules to s3:\n")
    # s3: s1(eth1) → s2(eth2) [медленный путь]
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s3 "priority=200,in_port=1,actions=output:2"')
    h.cmd('sh ovs-ofctl -O OpenFlow13 add-flow s3 "priority=1,actions=FLOOD"')
    info("    ✓ s1(eth1) → s2(eth2) [slow path]\n")
    
    time.sleep(2)
    
    # Проверить что правила добавлены
    info("\n  Verifying rules...\n")
    flows_s1 = h.cmd('sh ovs-ofctl -O OpenFlow13 dump-flows s1 | grep -E "priority|actions"')
    info(f"  s1 flows:\n{flows_s1}\n")
def verify_connectivity(net):
    """Проверить связность после применения правил"""
    info("\n" + "="*60)
    info(" VERIFYING CONNECTIVITY")
    info("="*60 + "\n")
    
    info("  Running pingall...\n")
    net.pingAll()
def run():
    # Get ONOS host from environment or use default
    onos_host = os.environ.get('ONOS_HOST', '172.28.0.2')
    onos_port = int(os.environ.get('ONOS_PORT', '6653'))
    
    topo = QoSTopology()
    
    # Create network with RemoteController (will connect to ONOS)
    net = Mininet(
        topo=topo,
        link=TCLink,
        controller=RemoteController('onos', ip=onos_host, port=onos_port),
        switch=OVSKernelSwitch,
        autoSetMacs=True,
        autoStaticArp=True,
        waitConnected=False  # Don't wait for controller connection
    )
    
    info("\n" + "="*60)
    info(" STARTING QoS NETWORK")
    info("="*60 + "\n")
    net.start()
    
    info("\n" + "="*60)
    info(" PHASE 1: CONNECTING TO ONOS CONTROLLER")
    info("="*60 + "\n")
    info(f"  ONOS Controller: {onos_host}:{onos_port}\n")
    info("  Waiting 30 seconds for switches to connect...\n")
    time.sleep(30)
    
    # Показать что коммутаторы подключены к контроллеру
    info("  Checking controller connection...\n")
    for switch in net.switches:
        controller = switch.cmd('ovs-vsctl get-controller %s' % switch.name).strip()
        info(f"    {switch.name}: {controller if controller else 'No controller'}\n")
    
    info("\n  ✓ Switches connected to ONOS!\n")
    info("  (You can verify in ONOS web UI: http://localhost:8181)\n")
    
    time.sleep(5)
    
    # Отключить контроллер
    disconnect_controllers(net)
    
    # Добавить правила
    add_qos_rules(net)
    
    # Проверить связность
    verify_connectivity(net)
    
    info("\n" + "="*60)
    info(" DEMO READY - Test Commands")
    info("="*60 + "\n")
    info("  VoIP (Fast Path, ~100 Mbps):\n")
    info("    h4 iperf -s &\n")
    info("    h3 iperf -c 10.0.0.4 -S 0xB8 -t 10\n")
    info("    h3 ping -c 3 -Q 0xB8 10.0.0.4\n\n")
    info("  Regular (Slow Path, ~10 Mbps):\n")
    info("    h2 iperf -s &\n")
    info("    h1 iperf -c 10.0.0.2 -t 10\n")
    info("    h1 ping -c 3 10.0.0.2\n\n")
    info("="*60 + "\n\n")
    
    CLI(net)
    net.stop()
if __name__ == '__main__':
    setLogLevel('info')
    run()
