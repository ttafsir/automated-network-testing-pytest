import json


def test_ntp_is_synchronised(host, helpers):
    """
    Arrange/Act: Retrieve facts from device and variables from inventory
    Assert: The configured ASN matches the inventory ASN
    """
    output = helpers.send_command(host.connection, "show ntp status | json")
    output_dict = json.loads(output)
    assert output_dict["json"]["status"] == "synchronised", "NTP is not synchronised"
