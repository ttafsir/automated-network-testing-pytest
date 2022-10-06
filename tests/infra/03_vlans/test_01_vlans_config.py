def test_vlans_match_intent(leaf_host, get_host_intent, get_connection, helpers):
    """
    Arrange/Act: retrieve "show vlan | json" output from device.
    Assert: Every VLAN from the intended config is deployed to the device.
    """
    # Arrange
    intended_vlans = get_host_intent(leaf_host.name).get("vlans")

    # Act/Assert
    with get_connection(leaf_host.name) as conn:
        output = helpers.send_command(conn, "show vlan | json")
        vlan_ids = [int(k) for k, _ in output["vlans"].items()]
        intended_vlan_ids = [int(k) for k, _ in intended_vlans.items()]
        assert all(
            vlan in vlan_ids for vlan in intended_vlan_ids
        ), f"expected: {intended_vlan_ids}. Found: {vlan_ids}. Diff: {set(intended_vlan_ids).difference(vlan_ids)}"
