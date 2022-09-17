from ipaddress import ip_interface

import pytest


def test_ethernet_link_neighbor_is_reachable(
    helpers, avd_p2p_link, get_connection, get_host_intent
):
    """
    Arrange: Load fabric p2p links and load device's structured configuration
    Act: Connect to device and ping from one end of the link to the other
    Assert: The link peer IPs are reachable on P2P links
    """
    # Arrange
    node_name = avd_p2p_link["Node"]
    node_interface = avd_p2p_link["Node Interface"]
    remote_ip = ip_interface(avd_p2p_link["Peer IP Address"])

    host_intent = get_host_intent(node_name)
    source_ip = ip_interface(
        host_intent["ethernet_interfaces"][node_interface].get("ip_address")
    )

    # Act
    with get_connection(node_name) as conn:
        output = helpers.send_command(
            conn, f"ping {remote_ip.ip} source {source_ip.ip} repeat 1"
        )
    # Assert
    assert "1 received" in output


def test_remote_loopback0_reachability_from_l3leafs(
    leaf_host, helpers, get_host_intent, avd_fabric_loopback, get_connection
):
    """
    Arrange: Retrieve configured loopback0 IPs from inventory
    Act: Ping each loopback IP from loopback0
    Assert: All loopback0 IPs can be reached from loopback0
    """
    if leaf_host.host_vars["type"] != "l3leaf":
        pytest.skip(reason="Test is only valid for l3 leaf")

    host_intent = get_host_intent(leaf_host.name)
    remote_ip = ip_interface(avd_fabric_loopback[1]["ip_address"])
    local_ip = ip_interface(
        host_intent["loopback_interfaces"]["Loopback0"]["ip_address"]
    )
    # Act
    with get_connection(leaf_host.name) as conn:
        output = helpers.send_command(
            conn, f"ping {remote_ip.ip} source {local_ip.ip} repeat 1"
        )
    # Assert
    assert "1 received" in output
