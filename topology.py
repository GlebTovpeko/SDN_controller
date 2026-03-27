from mininet.node import RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
from mininet.link import TCLink

def create_topology():
    net = Mininet(controller=RemoteController, link=TCLink)

    c0 = net.addController('c0',
                            controller=RemoteController,
                            ip='127.0.0.1',
                            port=6653)

    s1 = net.addSwitch('s1')

    h1 = net.addHost('h1', ip='10.0.1.1/24', defaultRoute='via 10.0>
    h2 = net.addHost('h2', ip='10.0.1.2/24', defaultRoute='via 10.0>

    h3 = net.addHost('h3', ip='10.0.2.1/24', defaultRoute='via 10.0>
    h4 = net.addHost('h4', ip='10.0.2.2/24', defaultRoute='via 10.0>

    net.addLink(h1, s1)
    net.addLink(h2, s1)
    net.addLink(h3, s1)
    net.addLink(h4, s1)

    net.start()
    print("Topology started")
    print("Work net:  h1=10.0.1.1, h2=10.0.1.2")
    print("Guest net: h3=10.0.2.1, h4=10.0.2.2")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_topology()