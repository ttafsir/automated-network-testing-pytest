import json
from pathlib import Path

import yaml
from netmiko import ConnectHandler

# Arrange
testbed_path = Path(__file__).parent.parent / "devices.yaml"
devices = yaml.safe_load(testbed_path.read_text())
expected_vlans = [4093, 4094, 110, 111, 3009]


# These are examples of bad test functions because a single test
# is used to verify all devices, and if any fails, the rest are
# not tested.
def test_bgp_enabled():
    for device in devices:
        conn_details = {k: v for k, v in device.items() if k != "hostname"}

        with ConnectHandler(**conn_details) as conn:
            # Act
            output = conn.send_command("show ip bgp summary")
            # Assert
            assert "BGP is disabled" not in output


def test_expected_vlans_exist():
    for device in devices:
        conn_details = {k: v for k, v in device.items() if k != "hostname"}

        with ConnectHandler(**conn_details) as conn:
            # Act
            output = conn.send_command("show vlan | json")
            vlan_ids = json.loads(output).get("vlans", {}).keys()
            # Assert
            for vlan in expected_vlans:
                assert str(vlan) in list(vlan_ids)
