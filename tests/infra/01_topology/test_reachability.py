from ipaddress import ip_interface


def test_ethernet_link_neighbor_is_reachable(helpers, avd_p2p_link, get_connection):
    """
    Arrange/Act:
    Assert: The link peer IPs are reachable on P2P links
    """
    node = (avd_p2p_link["Node"],)
    remote_ip = ip_interface(avd_p2p_link["Peer IP Address"])

    with get_connection(node) as conn:
        output = helpers.send_command(conn, f"ping {remote_ip.ip} repeat 1")

    assert "1 received" in output["stdout"]
