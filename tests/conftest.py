from pathlib import Path

import pytest
import yaml


def get_id(host_dict):
    return host_dict.pop("hostname")


def pytest_addoption(parser):
    parser.addoption(
        "--testbed", action="store", default="devices.yaml", help="path to testbed file"
    )


def pytest_generate_tests(metafunc):
    testbed_path = metafunc.config.getoption("testbed")

    if not testbed_path:
        pytest.fail("--testbed option is required.")

    if "device" in metafunc.fixturenames and testbed_path:
        path = Path(__file__).parent / Path(testbed_path)
        testbed = yaml.safe_load(path.read_text())
        metafunc.parametrize("device", testbed, ids=get_id)
