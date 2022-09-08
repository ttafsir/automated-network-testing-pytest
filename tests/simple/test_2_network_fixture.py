import os

import pytest
from netmiko import ConnectHandler


@pytest.fixture
def device_data():
    return {
        "host": "172.100.100.4",
        "username": os.environ.get("NETMIKO_USERNAME"),
        "password": os.environ.get("NETMIKO_PASSWORD"),
        "device_type": "arista_eos",
    }


@pytest.fixture
def connected_device(device_data):
    connected_device = ConnectHandler(**device_data)
    connected_device.enable()
    yield connected_device
    connected_device.disconnect()


def test_spanning_tree_mode_is_mstp(connected_device):
    output = connected_device.send_command("show run | include spanning-tree")
    assert "mstp" in output
