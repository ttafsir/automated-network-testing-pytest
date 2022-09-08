import json

import pytest
from netmiko import ConnectHandler

expected_vlans = [4093, 4094, 110, 111, 3009]


def test_bgp_enabled(device):
    conn_dict = {k: v for k, v in device.items() if k != "hostname"}
    with ConnectHandler(**conn_dict) as conn:
        output = conn.send_command("show ip bgp summary")
        assert "BGP is disabled" not in output


@pytest.mark.parametrize("vlan", expected_vlans)
def test_expected_vlans_exist(device, vlan):
    conn_dict = {k: v for k, v in device.items() if k != "hostname"}
    with ConnectHandler(**conn_dict) as conn:
        output = conn.send_command("show vlan | json")
        vlan_ids = json.loads(output).get("vlans", {}).keys()
        assert str(vlan) in list(vlan_ids)
