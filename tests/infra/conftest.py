import pytest


@pytest.fixture(scope="module", name="l3_host")
def l3_host_fixture(host, get_host_intent):
    """
    Fixture to get an ansible_host to test against.
    See the pytest_generate_tests hook for how this is used.
    """
    host_intent = get_host_intent(str(host.name))
    if host_intent.get("router_bgp") is not None:
        return host
    pytest.xfail("BGP is not expected on this device.")
