from pathlib import Path

import pytest

from .framework import (
    AnsibleTestHost,
    load_avd_structured_configs,
    parse_ansible_inventory_cli,
)


@pytest.fixture(scope="session", ids=lambda d: d.name)
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


@pytest.fixture(scope="session")
def avd_structured_configs(request):
    """
    Load yaml data files from inventory_dir/intended/structured_configs,
    where each file represents a structured config. Returns  a dictionary
    with the file stem as the key and the value as the yaml data.
    """
    inventory_path = Path(request.config.getoption("ansible_inventory"))
    inventory_dir = (
        inventory_path.parent if inventory_path.is_file() else inventory_path
    )
    return load_avd_structured_configs(inventory_dir)


@pytest.fixture(scope="session", name="get_host_intent")
def host_intent_fixture(avd_structured_configs):
    """Get the device's intent data from"""

    def _get_host_intent(hostname):
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


def get_ids(host_obj: AnsibleTestHost) -> str:
    return str(host_obj.name)


def pytest_generate_tests(metafunc):
    """
    Generate tests based on ansible inventory and host to test against.
    This is a pytest hook. See https://docs.pytest.org/en/latest/reference.html#hooks
    """
    inventory_path = metafunc.config.getoption("inventory_path")
    if not inventory_path:
        pytest.fail("--inventory-path option is required.")
    host_or_group = metafunc.config.getoption("hosts")

    # The "ansible_host" can be called as a parameter in any test function to run against the
    # host(s) specified using the --hosts option or the "all" host if no --hosts option is
    # specified.
    if "test_host" in metafunc.fixturenames and inventory_path is not None:

        # Extract host and host_vars from ansible inventory. We get a generator that
        # yields tuples of (Host, host_vars) where Host is an ansible.inventory.host.Host
        # object and host_vars is a dict of host_vars. THERE IS PROBABLY A BETTER WAY TO DO THIS.
        inventory = parse_ansible_inventory_cli(
            host_or_group=host_or_group, inventory=inventory_path
        )
        test_hosts = [
            AnsibleTestHost(*h) for h in sorted(inventory, key=lambda x: x[0].name)
        ]

        metafunc.parametrize(
            "test_host",
            test_hosts,
            scope="session",
            ids=get_ids,
            indirect=True,
        )
