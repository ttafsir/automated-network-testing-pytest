import json
from pathlib import Path

import yaml
import pytest
from netmiko import ConnectHandler

testbed_path = Path(__file__).parent.parent / "devices.yaml"
devices = yaml.safe_load(testbed_path.read_text())
expected_vlans = [4093, 4094, 110, 111, 3009]


@pytest.mark.parametrize("device", devices, ids=lambda x: x["hostname"])
def test_bgp_enabled(device):
    # Arrange
    conn_dict = {k: v for k, v in device.items() if k != "hostname"}
    with ConnectHandler(**conn_dict) as conn:
        # Act
        output = conn.send_command("show ip bgp summary")
        # Assert
        assert "BGP is disabled" not in output


@pytest.mark.parametrize("vlan", expected_vlans)
@pytest.mark.parametrize("device", devices, ids=lambda x: x["hostname"])
def test_expected_vlans_exist(device, vlan):
    # Arrange
    conn_dict = {k: v for k, v in device.items() if k != "hostname"}
    with ConnectHandler(**conn_dict) as conn:
        # Act
        output = conn.send_command("show vlan | json")
        vlan_ids = json.loads(output).get("vlans", {}).keys()
        # Assert
        assert str(vlan) in list(vlan_ids)
