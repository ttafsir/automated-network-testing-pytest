import os
import sys
from typing import Any, Generator, Optional, Tuple

try:
    from ansible import context
    from ansible.cli import CLI
    from ansible.cli.inventory import InventoryCLI
    from ansible.inventory.host import Host
except ImportError:
    sys.exit("Ansible is not installed. Please install by running: pip install ansible")

try:
    from netmiko import ConnectHandler
except ImportError:
    sys.exit("netmiko is not installed. Please install by running: pip install netmiko")

InventoryCLIResult = Tuple[Host, dict]


class AnsibleInventoryCLI(InventoryCLI):
    """
    We're subclassing the ansible.cli.inventory.InventoryCLI to build a
    way to iterate over the host vars as Ansible sees them.
    """

    def iter_host_vars(self):
        """Iterate over host vars as Ansible sees them"""
        CLI.run(self)
        self.loader, self.inventory, self.vm = self._play_prereqs()

        for host in self.inventory.get_hosts(context.CLIARGS["host"]):
            yield host, self._get_host_variables(host=host)


class AnsibleTestHost:
    """
    Test host class to be used with pytest.
    """

    def __init__(self, name: str, host_vars: dict[str, Any]):
        self.name = name
        self.host_vars = host_vars or {}
        self.connection = None

    def _get_device_platform(self, name: str) -> str:
        """Get device platform from name"""
        mapping = {
            "eos": "arista_eos",
            "ios": "cisco_iosxe",
            "nxos": "cisco_nxos",
            "iosxr": "cisco_iosxr",
        }
        return mapping.get(name.lower())

    @property
    def platform(self):
        """Get device platform"""
        return self._get_device_platform(self.host_vars.get("ansible_network_os", ""))

    def init_connection(self):
        """Get SSH connection to device"""
        if self.connection is None:
            self.connection = ConnectHandler(
                host=self.host_vars["ansible_host"],
                port=int(self.host_vars.get("ansible_port", 22)),
                username=os.environ.get("ANSIBLE_USER"),
                password=os.environ.get("ANSIBLE_PASSWORD"),
                device_type=self.platform
            )


def parse_ansible_inventory_cli(
    host_or_group: str = "all", inventory: str = None
) -> Optional[Generator[InventoryCLIResult, None, None]]:
    """
    Run Ansible Inventory to get host vars.

    Args:
        host_or_group: host or group to get vars for
        inventory: path to inventory file

    Returns:
        Generator of (Host, host_vars) tuples
    """
    if inventory is None:
        return None
    args = ["ansible-inventory", "--inventory", inventory, "--host", host_or_group]
    cli = AnsibleInventoryCLI(args)
    return cli.iter_host_vars()
