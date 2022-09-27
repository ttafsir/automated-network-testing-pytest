import json
import logging
import typing
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

import pytest
from netmiko import BaseConnection

from .framework import (
    AnsibleTestHost,
    load_avd_fabric_data,
    load_avd_structured_configs,
    parse_ansible_inventory_cli,
)

test_logger = logging.getLogger()
test_logger.setLevel(logging.INFO)


class Helpers:
    """
    Helper class to provide helper fixtures
    """

    @staticmethod
    @lru_cache(maxsize=128)
    def send_command(connection: BaseConnection, command: str) -> str:
        """
        Send command to host and return output
        """
        output = connection.send_command_timing(command, read_timeout=600)

        # log test function, command, and output
        test_logger.info("Sending command: %s to %s", command, connection.host)
        test_logger.info("Output: %s", output)
        try:
            return json.loads(output)
        except json.decoder.JSONDecodeError:
            test_logger.warning("Command output is not JSON: %s", output)
            return output

@pytest.fixture
def helpers():
    """Helper fixtures to manage connections to and output from devices"""
    return Helpers


@pytest.fixture(scope="session", ids=lambda device: device.name)
def test_host(request):
    return request.param


@pytest.fixture(scope="session")
def host(test_host):
    """
    Returns the connection and performs teardown for each host needed in tests
    """
    test_host.init_connection()
    test_host.connection.enable()
    yield test_host
    if test_host.connection is not None:
        test_host.connection.disconnect()
        test_host.connection = None


@pytest.fixture(scope="session")
def get_connection():
    """
    Fixture factory to retrieve host from tests that cannot use host fixture directly
    """

    @contextmanager
    def _get_connection(hostname: str):
        host = AnsibleTestHost.get_host(hostname)
        if host.connection is None:
            host.init_connection()
            host.connection.enable()
        yield host.connection
        if host.connection is not None:
            host.connection.disconnect()
            host.connection = None

    yield _get_connection


@pytest.fixture(scope="session", name="inventory_path")
def inventory_path_fixture(request):
    return Path(request.config.getoption("inventory_path"))


@pytest.fixture(scope="session", name="rootdir")
def rootdir_path_fixture(request):
    return Path(request.config.rootdir)


@pytest.fixture(scope="session")
def avd_structured_configs(inventory_path, rootdir):
    """
    Load yaml data files from inventory_dir/intended/structured_configs,
    where each file represents a structured config. Returns  a dictionary
    with the file stem as the key and the value as the yaml data.
    """
    inventory_dir = (
        inventory_path.parent if inventory_path.is_file() else inventory_path
    )
    return load_avd_structured_configs(inventory_dir, rootdir=Path(rootdir))


@pytest.fixture(scope="session", name="get_host_intent")
def host_intent_fixture(avd_structured_configs):
    """Get the device's intent data from"""

    def _get_host_intent(hostname: str) -> typing.Optional[dict]:
        intent = avd_structured_configs.get(hostname)
        if intent is None:
            pytest.fail(f"Could not load host intent for: {hostname}")
        return intent

    return _get_host_intent


def get_avd_fabric_loopbacks(inventory_dir: Path) -> typing.Iterable[tuple]:
    """Retrieve the loopback0 address from intented configs for the fabric"""
    structured_intent_data = load_avd_structured_configs(inventory_dir)
    return [
        (hostname, host_intent["loopback_interfaces"]["Loopback0"])
        for hostname, host_intent in structured_intent_data.items()
        if host_intent.get("loopback_interfaces")
    ]


def pytest_addoption(parser):
    """
    Add options to control ansible inventory and host to test against.
    This is a pytest hook. See https://docs.pytest.org/en/latest/reference.html#hooks

    The options are:
    - inventory-path: path to ansible inventory file
    - hosts: host or group to test against

    These can be used in the following ways:
    - pytest --inventory-path=inventory
    - pytest --inventory-path=inventory.yml --hosts=eos,ios
    """
    parser.addoption(
        "--inventory-path",
        action="store",
        default="inventory",
        help="path to ansible",
    )
    parser.addoption(
        "--hosts",
        action="store",
        default="all",
        help="host or group to test",
    )
    parser.addoption(
        "--fabric",
        action="store",
        help="AVD fabric name",
    )


def get_ids(host_obj: AnsibleTestHost) -> str:
    return host_obj.name


def get_topology_ids(topology_dict: dict) -> str:
    """ID function for topology parametrization"""
    return (
        f"{topology_dict['Node']}-{topology_dict['Node Interface']}:"
        f"{topology_dict['Peer Node']}-{topology_dict['Peer Interface']}"
    )


def get_loopback_ids(interface_data: tuple) -> str:
    """ID function for Lo0 intent parametrization"""
    hostname, interface = interface_data
    ip = interface.get("ip_address") if interface else "no-IP"
    return f"({hostname})-lo0-{ip}"


def pytest_generate_tests(metafunc):
    """
    Generate tests based on ansible inventory and host to test against.
    This is a pytest hook. See https://docs.pytest.org/en/latest/reference.html#hooks
    """
    inventory_path = metafunc.config.getoption("inventory_path")
    if not inventory_path:
        pytest.fail("--inventory-path option is required.")
    host_or_group_opt = metafunc.config.getoption("hosts")
    fabric_opt = metafunc.config.getoption("fabric")

    # Extract host and host_vars from ansible inventory. We get a generator that
    # yields tuples of (Host, host_vars) where Host is an ansible.inventory.host.Host
    # object and host_vars is a dict of host_vars. THERE IS PROBABLY A BETTER WAY TO DO THIS.
    inventory = parse_ansible_inventory_cli(
        host_or_group=host_or_group_opt, inventory=inventory_path
    )

    # The "ansible_host" can be called as a parameter in any test function to run against the
    # host(s) specified using the --hosts option or the "all" host if no --hosts option is
    # specified.
    test_hosts = [
        AnsibleTestHost.get_host(str(h.name), host_vars=host_vars)
        for h, host_vars in sorted(inventory, key=lambda x: x[0].name)
    ]

    # Parametrize tests with hosts from the Ansible inventory. Includes all hosts.
    if "test_host" in metafunc.fixturenames and inventory_path is not None:
        metafunc.parametrize(
            "test_host",
            test_hosts,
            scope="session",
            ids=get_ids,
            indirect=True,
        )

    # Use `leaf_host` for tests to require just leafs
    if "leaf_host" in metafunc.fixturenames and fabric_opt is not None:
        leafs = [x for x in test_hosts if x.host_vars["type"] in ("l2leaf", "l3leaf")]
        metafunc.parametrize("leaf_host", leafs, scope="module", ids=get_ids)

    # Use `leaf_host` for tests to require just leafs
    if "l3_host" in metafunc.fixturenames and fabric_opt is not None:
        leafs = [x for x in test_hosts if x.host_vars["type"] in ("l3leaf", "spine")]
        metafunc.parametrize("l3_host", leafs, scope="module", ids=get_ids)

    # Use `spine_host` for tests to require just spines
    if "spine_host" in metafunc.fixturenames and fabric_opt is not None:
        leafs = [x for x in test_hosts if x.host_vars["type"] == "spine"]
        metafunc.parametrize("spine_host", leafs, scope="module", ids=get_ids)

    if "avd_fabric_loopback" in metafunc.fixturenames and fabric_opt is not None:
        loopbacks = get_avd_fabric_loopbacks(Path(inventory_path))
        metafunc.parametrize("avd_fabric_loopback", loopbacks, ids=get_loopback_ids)

    # Load AVD topology design documentation data to parametrize any tests that requests
    # the `topology` fixture as a dependency.
    if "avd_topology" in metafunc.fixturenames and fabric_opt is not None:
        if fabric_topology := load_avd_fabric_data(
            "topology",
            inventory_dir=Path(inventory_path),
            rootdir=metafunc.config.rootdir,
            fabric=fabric_opt,
        ):
            metafunc.parametrize(
                "avd_topology", fabric_topology, scope="session", ids=get_topology_ids
            )
        else:
            metafunc.parametrize("avd_topology", [], ids=["missing-topology-file"])

    # Load AVD P2P design documentation data to parametrize any tests that requests
    # the `avd_p2p_link` fixture as a dependency.
    if "avd_p2p_link" in metafunc.fixturenames and fabric_opt is not None:
        if fabric_p2p_links := load_avd_fabric_data(
            "p2p",
            inventory_dir=Path(inventory_path),
            rootdir=metafunc.config.rootdir,
            fabric=fabric_opt,
        ):
            metafunc.parametrize(
                "avd_p2p_link", fabric_p2p_links, scope="session", ids=get_topology_ids
            )
        else:
            metafunc.parametrize("avd_p2p_link", [], ids=["missing-p2p-file"])
