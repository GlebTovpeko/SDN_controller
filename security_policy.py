import requests
import json

ONOS_IP = "localhost"
ONOS_PORT = 8181
BASE_URL = f"http://{ONOS_IP}:{ONOS_PORT}/onos/v1"
AUTH = ("karaf", "karaf")
HEADERS = {"Content-Type": "application/json"}

def get_device_id():
    resp = requests.get(f"{BASE_URL}/devices", auth=AUTH)
    devices = resp.json()["devices"]
    if not devices:
        print("Switches not found! Run Mininet first.")
        return None
    device_id = devices[0]["id"]
    print(f"Switch found: {device_id}")
    return device_id

def add_flow_rule(device_id, priority, src_ip, dst_ip, action="DROP"):
    if action == "DROP":
        instructions = []
    else:
        instructions = [{"type": "OUTPUT", "port": "NORMAL"}]

    flow = {
        "priority": priority,
        "timeout": 0,
        "isPermanent": True,
        "deviceId": device_id,
        "treatment": {
            "instructions": instructions
        },
        "selector": {
            "criteria": [
                {"type": "ETH_TYPE", "ethType": "0x0800"},
                {"type": "IPV4_SRC", "ip": src_ip},
                {"type": "IPV4_DST", "ip": dst_ip}
            ]
        }
    }

    resp = requests.post(
        f"{BASE_URL}/flows/{device_id}",
        data=json.dumps({"flows": [flow]}),
        headers=HEADERS,
        auth=AUTH
    )

    if resp.status_code in [200, 201]:
        print(f"Rule added: {src_ip} -> {dst_ip} = {action}")
    else:
        print(f"Error: {resp.status_code} - {resp.text}")

def apply_security_policy():
    device_id = get_device_id()
    if not device_id:
        return

    add_flow_rule(device_id, 40000, "10.0.2.0/24", "10.0.1.1/32", "DROP")
    add_flow_rule(device_id, 40000, "10.0.2.0/24", "10.0.1.2/32", "DROP")
    add_flow_rule(device_id, 40000, "10.0.2.0/24", "10.0.1.0/24", "DROP")

    print("Policy applied!")

def show_flows(device_id=None):
    if not device_id:
        device_id = get_device_id()
    resp = requests.get(f"{BASE_URL}/flows/{device_id}", auth=AUTH)
    flows = resp.json().get("flows", [])
    print(f"Total flows: {len(flows)}")
    for f in flows:
        print(f"  Priority {f['priority']}: {f['selector']} -> {f['treatment']}")

if __name__ == "__main__":
    apply_security_policy()