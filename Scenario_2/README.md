# QoS SDN Project

Simple production setup with ONOS + Mininet.

## Quick Start

```bash
# Install task
yay -S task

# Build and start
go-task build
go-task up

# Enter Mininet
task shell

# Inside container:
python3 qos_topology.py

# In another terminal:
python src/qos_controller.py