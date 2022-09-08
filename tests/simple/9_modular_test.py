import json

import pytest

expected_vlans = [4093, 4094, 110, 111, 3009]


def test_bgp_enabled(device):
    output = device.send_command("show ip bgp summary")  # Act
    assert "BGP is disabled" not in output  # Assert


@pytest.mark.parametrize("vlan", expected_vlans)
def test_expected_vlans_exist(device, vlan, helpers):
    # Act
    output = helpers.send_command(device, "show vlan | json")
    vlan_ids = json.loads(output).get("vlans", {}).keys()
    # Assert
    assert str(vlan) in list(vlan_ids)


def test_spanning_tree_mode_is_mstp(device, helpers):
    # Act
    output = helpers.send_command(device, "show run | include spanning-tree")
    # Assert
    assert "mstp" in output
