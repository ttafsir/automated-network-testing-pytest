import pytest


def test_every_link_in_avd_topology_is_connected(avd_topology, get_connection, helpers):
    """
    Arrange/Act: Get device connection for link under test. Connect
        to the devices and gather "show interfaces" output
    Assert: Verify that link is connected
    """
    # Arrange
    node = avd_topology["Node"]
    node_interface = avd_topology["Node Interface"]

    # Act
    with get_connection(node) as conn:
        output = helpers.send_command(conn, "show interfaces | json")
        # Assert
        assert (
            output["interfaces"][node_interface]["interfaceStatus"] == "connected"
        ), "Link is not connected"


def test_lldp_neighbors_match_intent(avd_topology, get_connection, helpers):
    """
    Arrange/Act: Get device connection for link under test. Get
        link's intended peer data. Connect to the devices and
        gather "show lldp neighbors" output
    Assert: Verify that the expected peer and port are found
    """
    # Arrange
    node = avd_topology["Node"]
    node_interface = avd_topology["Node Interface"]
    peer_node = avd_topology["Peer Node"]
    peer_interface = avd_topology["Peer Interface"]

    peer_type = avd_topology["Peer Type"]
    if peer_type == "server":
        pytest.skip(reason="LLDP is not properly configured on servers")

    # Act
    with get_connection(node) as conn:
        output = helpers.send_command(conn, "show lldp neighbors | json")
        neighbors = [
            (n["neighborDevice"], n["neighborPort"])
            for n in output["lldpNeighbors"]
            if n["port"] == node_interface
        ]

    # Assert
    if not neighbors:
        pytest.fail(f"No neighbors found on: {node_interface}")
    assert (
        peer_node,
        peer_interface,
    ) in neighbors, f"Expected: {peer_node}, {peer_interface}"


def test_l3_p2p_links_have_correct_ips(avd_p2p_link, get_connection, helpers):
    """
    Arrange/Act: Get device connection for link under test. Connect
        to the devices and gather "show ip interface" output
    Assert: Verify that link has an IP address
    """
    # Arrange
    left_node_data = [
        avd_p2p_link["Node"],
        avd_p2p_link["Node Interface"],
        avd_p2p_link["Leaf IP Address"],
    ]

    right_node_data = [
        avd_p2p_link["Peer Node"],
        avd_p2p_link["Peer Interface"],
        avd_p2p_link["Peer IP Address"],
    ]

    # Act for both sides of the link
    for node, intf, ip in (left_node_data, right_node_data):
        with get_connection(node) as conn:
            output = helpers.send_command(conn, "show ip interface | json")

            # Assert: Is the interface IP'ed?
            try:
                output["interfaces"][intf]
            except KeyError:
                pytest.fail(f"{node}-{intf} has no configured IP")

            # Assert: Does the IP match our design?
            assert (
                output["interfaces"][intf]["interfaceAddress"]["primaryIp"]["address"]
                == ip.split("/")[0]
            )
