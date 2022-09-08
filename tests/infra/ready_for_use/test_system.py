import json


def test_model_is_virtual(host):
    """
    Arrange/Act: Retrieve show version output from device
    Assert: Verify that the device platform is a virtual device
    """
    output = host.connection.send_command("show version | json")
    output_dict = json.loads(output)
    assert output_dict["modelName"] == "cEOSLab"


def test_software_version(host, get_host_intent):
    """
    Arrange/Act: Retrieve facts from device and variables from inventory
    Assert: The current matches the inventory version
    """
    host_intent = get_host_intent(host.name)
    output = host.connection.send_command("show version | json")
    output_dict = json.loads(output)
    assert host_intent["version"] in output_dict["version"]
