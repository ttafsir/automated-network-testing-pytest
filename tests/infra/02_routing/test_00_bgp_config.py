def test_bgp_expected_asn_is_configured(
    l3_host, helpers, get_host_intent, get_connection
):
    """
    Arrange/Act: retrieve "ip bgp summary" output from device. Retrieve
        BGP intent from AVD intended design.
    Assert: The configured ASN matches the inventory ASN
    """
    # Arrange
    host_intent = get_host_intent(l3_host.name)
    expected_bgp_as = host_intent["router_bgp"]["as"]

    # Act
    with get_connection(l3_host.name) as conn:
        output = helpers.send_command(conn, "show ip bgp summary | json")

    # Assert
    assert (
        actual := output["vrfs"]["default"]["asn"] == expected_bgp_as
    ), f"ASN: {actual} != {expected_bgp_as}"


def test_bgp_multi_agent_is_configured(l3_host, helpers, get_connection):
    """
    Arrange/Act: retrieve "ip route summary" output from device.
    Assert: The configured ArBGP multi-agent is enabled
    """
    with get_connection(l3_host.name) as conn:
        output = helpers.send_command(conn, "show ip route summary")
        assert "multi-agent" in output
