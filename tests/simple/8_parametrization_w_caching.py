import json
from functools import lru_cache
from pathlib import Path

import pytest
import yaml
from netmiko import BaseConnection, ConnectHandler

# Arrange
testbed_path = Path(__file__).parent.parent / "devices.yaml"
tesbed = yaml.safe_load(testbed_path.read_text())
expected_vlans = [4093, 4094, 110, 111, 3009]


@lru_cache(maxsize=128)
def send_command(host: BaseConnection, command: str) -> str:
    return host.send_command(command)


@pytest.fixture(params=tesbed, ids=lambda d: d["hostname"], scope="module")
def device(request):
    device_dict = request.param
    conn_dict = {k: v for k, v in device_dict.items() if k != "hostname"}
    connected_device = ConnectHandler(**conn_dict)
    yield connected_device
    connected_device.disconnect()


def test_bgp_enabled(device):
    output = device.send_command("show ip bgp summary")  # Act
    assert "BGP is disabled" not in output  # Assert


@pytest.mark.parametrize("vlan", expected_vlans)
def test_expected_vlans_exist(device, vlan):
    # Act
    output = send_command(device, "show vlan | json")
    vlan_ids = json.loads(output).get("vlans", {}).keys()
    print(send_command.cache_info())
    # Assert
    assert str(vlan) in list(vlan_ids)
