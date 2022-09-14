import re
import typing
from contextlib import contextmanager
from pathlib import Path

import pytest

from .framework import (
    AnsibleTestHost,
    load_avd_fabric_data,
    load_avd_structured_configs,
    parse_ansible_inventory_cli,
)


@pytest.fixture(scope="session", ids=lambda device: device.name)
def test_host(request):
    return request.param


@pytest.fixture(scope="session")
def host(test_host):
    """
    Connection setup and teardown for
    each host needed in tests.
    """
    test_host.init_connection()
    test_host.connection.enable()
    yield test_host
    test_host.connection.disconnect()
    test_host.connection = None


@pytest.fixture(scope="session")
def get_connection():
    @contextmanager
    def _get_connection(hostname: str):
        host = AnsibleTestHost.get_host(hostname)
        if host.connection is None:
            host.init_connection()
            host.connection.enable()
        yield host.connection
        host.connection.disconnect()
        host.connection = None

    yield _get_connection


@pytest.fixture(scope="session", name="inventory_path")
def inventory_path_fixture(request):
    return Path(request.config.getoption("inventory_path"))


@pytest.fixture(scope="session", name="rootdir")
def rootdir_path_fixture(request):
    return Path(request.config.rootdir)


@pytest.fixture(scope="session", name="avd_p2p_links")
def avd_p2p_links_fixture(request):
    config = request.config
    return config.avd_p2p_links


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


def pytest_addoption(parser):
    """
    Add options to control ansible inventory and host to test against.
    This is a pytest hook. See https://docs.pytest.org/en/latest/reference.html#hooks

    The options are:
    - inventory-path: path to ansible inventory file
    - hosts: host or group to test against

    These can be used in the following ways:
    - pytest --inventory-path=inventory.yml
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


def get_topology_ids(topology_dict: dict):
    """ID function for pytest parametrization"""
    return (
        f"{topology_dict['Node']}-{topology_dict['Node Interface']}:"
        f"{topology_dict['Peer Node']}-{topology_dict['Peer Interface']}"
    )


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
    if "test_host" in metafunc.fixturenames and inventory_path is not None:
        metafunc.parametrize(
            "test_host",
            test_hosts,
            scope="session",
            ids=get_ids,
            indirect=True,
        )

    # Load AVD fabric data so that we can use it to parametrize any tests that requests
    # the `topology` fixture as a dependency.
    if "topology" in metafunc.fixturenames and fabric_opt is not None:
        fabric_topology = load_avd_fabric_data(
            "topology",
            inventory_dir=Path(inventory_path),
            rootdir=metafunc.config.rootdir,
            fabric=fabric_opt,
        )

        # The "topology" fixture can be called as a parameter in any test function
        # to run against the topology specified using the --fabric option.
        metafunc.parametrize(
            "topology", fabric_topology, scope="session", ids=get_topology_ids
        )

    if "avd_p2p_links" in metafunc.fixturenames and fabric_opt is not None:
        fabric_p2p_links = load_avd_fabric_data(
            "p2p",
            inventory_dir=Path(inventory_path),
            rootdir=metafunc.config.rootdir,
            fabric=fabric_opt,
        )
        metafunc.config.avd_p2p_links = fabric_p2p_links
