import json

import pytest


@pytest.mark.parametrize(
    "key, expected_value",
    [
        ("state", "active"),
        ("negStatus", "connected"),
    ],
)
def test_mlag_state_and_status(leaf_host, helpers, get_connection, key, expected_value):
    """
    Arrange/Act: Retrieve mlag operational state from device
    Assert: MLAG is active and connected on l2 and l3 leafs
    """
    # Act
    with get_connection(leaf_host.name) as conn:
        output = helpers.send_command(conn, "show mlag detail | json")
        output_dict = json.loads(output)

    # Assert
    assert output_dict[key] == expected_value, f"Expected '{key}' == '{expected_value}'"


def test_mlag_configuration_matches_intent(
    leaf_host, helpers, get_connection, get_host_intent
):
    """
    Arrange: Load intent for leaf devices
    Act: Retrieve mlag configuration state from leaf
    Assert: MLAG configuration matches intended configuration
    """
    host_intent = get_host_intent(leaf_host.name)
    mlag_intent = host_intent["mlag_configuration"]

    with get_connection(leaf_host.name) as conn:
        output = helpers.send_command(conn, "show mlag detail | json")
        output_dict = json.loads(output)

    assert (
        output_dict["domainId"] == mlag_intent["domain_id"]
        and output_dict["localInterface"] == mlag_intent["local_interface"]
        and output_dict["peerLink"] == mlag_intent["peer_link"]
        and output_dict["peerAddress"] == mlag_intent["peer_address"]
        and output_dict["reloadDelay"] == mlag_intent["reload_delay_mlag"]
        and output_dict["reloadDelayNonMlag"] == mlag_intent["reload_delay_non_mlag"]
    )
