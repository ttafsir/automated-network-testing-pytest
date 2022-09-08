# from functools import lru_cache
# from pathlib import Path

# import pytest
# import yaml
# from netmiko import BaseConnection, ConnectHandler

# # Arrange
# testbed_path = Path(__file__).parent.parent / "devices.yaml"
# tesbed = yaml.safe_load(testbed_path.read_text())


# @pytest.fixture(params=tesbed, ids=lambda d: d["hostname"], scope="module")
# def device(request):
#     device_dict = request.param
#     conn_dict = {k: v for k, v in device_dict.items() if k != "hostname"}
#     connected_device = ConnectHandler(**conn_dict)
#     connected_device.enable()
#     yield connected_device
#     connected_device.disconnect()


# class Helpers:
#     """
#     Helper class to provide helper fixtures
#     """
#     @staticmethod
#     @lru_cache(maxsize=128)
#     def send_command(host: BaseConnection, command: str) -> str:
#         return host.send_command(command)


# @pytest.fixture
# def helpers():
#     """Helper fixtures to manage connection to devices
#     """
#     return Helpers
