import json


def test_device_model_is_correct(host):
    """
    Arrange/Act: Retrieve show version output from device
    Assert: Verify that we have the correct device platform
    """
    output = host.connection.send_command("show version | json")
    output_dict = json.loads(output)
    assert output_dict["modelName"] == "cEOSLab"


def test_software_version(host):
    """
    Arrange/Act: Retrieve host vars/get show version output from device
    Assert: The version on the device matches the version in host_vars
    """
    output = host.connection.send_command("show version | json")
    output_dict = json.loads(output)
    assert host.host_vars.get("version") in output_dict["version"]


def test_hostname_matches_intended(host):
    """
    Arrange/Act: Retrieve host vars/get hostname from show run output
    Assert: The configured hostname matches the intended hostname
    """
    output = host.connection.find_prompt()
    hostname = output.replace("#", "")
    assert str(host.name) == hostname
