def test_device_model_is_correct(host, helpers):
    """
    Arrange/Act: Retrieve show version output from device
    Assert: Verify that we have the correct device platform
    """
    output = helpers.send_command(host.connection, "show version | json")
    assert output["modelName"] == "cEOSLab"


def test_software_version(host, helpers):
    """
    Arrange/Act: Retrieve host vars/get show version output from device
    Assert: The version on the device matches the version in host_vars
    """
    output = helpers.send_command(host.connection, "show version | json")
    assert host.host_vars.get("version") in output["version"]


def test_hostname_matches_intended(host):
    """
    Arrange/Act: Retrieve host vars/get hostname from show run output
    Assert: The configured hostname matches the intended hostname
    """
    output = host.connection.find_prompt()
    hostname = output.replace("#", "")
    assert str(host.name) == hostname
