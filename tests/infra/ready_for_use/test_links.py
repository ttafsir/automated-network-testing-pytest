import json

import pytest


def test_every_link_in_topology_is_connected(topology, get_connection):
    """
    Arrange/Act: Get device connection for link under test. Connect
        to the devices and gather "show interfaces" output
    Assert: Verify that link is connected
    """
    # Arrange
    node = topology["Node"]
    node_interface = topology["Node Interface"]

    # Act
    with get_connection(node) as conn:
        output = conn.send_command("show interfaces | json")
        output_dict = json.loads(output)

        # Assert
        assert (
            output_dict["interfaces"][node_interface]["interfaceStatus"] == "connected"
        ), "Link is not connected"


def test_lldp_neighbors_match(topology, get_connection):
    """
    Arrange/Act: Get device connection for link under test. Get
        link's intended peer data. Connect to the devices and
        gather "show lldp neighbors" output
    Assert: Verify that the expected peer and port are found
    """
    # Arrange
    node = topology["Node"]
    node_interface = topology["Node Interface"]
    peer_node = topology["Peer Node"]
    peer_interface = topology["Peer Interface"]

    # Act
    with get_connection(node) as conn:
        output = conn.send_command("show lldp neighbors | json")
        output_dict = json.loads(output)
        neighbors = [
            (n["neighborDevice"], n["neighborPort"])
            for n in output_dict["lldpNeighbors"]
            if n["port"] == node_interface
        ]

    # Assert
    if not neighbors:
        pytest.fail(f"No neighbors found on: {node_interface}")
    assert (
        peer_node,
        peer_interface,
    ) in neighbors, f"Expected: {peer_node}, {peer_interface}"


def test_l3_p2p_links_have_ip_addresses(avd_p2p_links, get_connection):
    """
    Arrange/Act: Get device connection for link under test. Connect
        to the devices and gather "show ip interface" output
    Assert: Verify that link has an IP address
    """
    ...
