import pytest
from my_module import vlan_range


@pytest.mark.parametrize(
    "test_input,expected",
    [
        (["1", "2", "3", "5", "6", "7", "10", "11", "12"], "1-3,5-7,10-12"),
        (["1", "2", "3", "4", "5", "6", "7", "8", "9"], "1-9"),
        (["1"], "1"),
        ([], ""),
        (["1", "2", "3", "5", "6", "7", "10", "11", "12"], "1-3,5-7,10-12"),
    ],
)
def test_vlan_range(test_input, expected):
    assert vlan_range(test_input) == expected
