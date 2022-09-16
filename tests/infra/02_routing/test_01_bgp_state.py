import pytest
import json


def test_bgp_enabled(l3_host, get_connection, helpers):
    """
    Arrange/Act: retrieve "show ip bgp summary" output from device.
    Assert: BGP process is enabled
    """
    with get_connection(l3_host.name) as conn:
        output = helpers.send_command(conn, "show ip bgp summary")
        assert "BGP is disabled" not in output


@pytest.mark.parametrize(
    "show_command",
    ["show ip bgp summary | json", "show bgp evpn summary | json"],
    ids=["bgp", "evpn"],
)
def test_bgp_expected_peers_are_established(l3_host, helpers, get_connection, show_command, get_host_intent):
    """
    Arrange/Act: retrieve IPv4 and evpn BGP output from device. Retrieve
        BGP intent from AVD intended design.
    Assert: The configured expected peers are established for IPv4 and EVPN
    """
    host_intent = get_host_intent(l3_host.name)
    expected_peers = host_intent["router_bgp"]["neighbors"]

    with get_connection(l3_host.name) as conn:
        output = helpers.send_command(conn, show_command)
        output_dict = json.loads(output)
        actual_peers = output_dict["vrfs"]["default"]["peers"]

    assert (
        actual_peers[neighbor]["peerState"] == "Established"
        for neighbor, _ in expected_peers.items()
    )
