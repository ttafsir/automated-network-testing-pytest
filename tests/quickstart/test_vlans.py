from my_module import vlan_range


def test_vlan_range_non_consecutive():
    test_range = vlan_range(["1", "2", "3", "5", "6", "7", "10", "11", "12"])
    assert test_range == "1-3,5-7,10-12"


def test_vlan_range_consecutive():
    test_range = vlan_range(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
    assert test_range == "1-9"


def test_vlan_range_single():
    test_range = vlan_range(["1"])
    assert test_range == "1"


def test_vlan_range_empty():
    test_range = vlan_range([])
    assert test_range == ""


def test_vlan_range_multiple_non_consecutive():
    test_range = vlan_range(["1", "2", "3", "5", "6", "7", "10", "11", "12"])
    assert test_range == "1-3,5-7,10-12"
