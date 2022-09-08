def add_numbers(a, b):
    return a + b


def test_add_numbers():
    assert add_numbers(1, 2) == 4


def test_strings_match():
    assert "presented by Tafsir" == "presented by TafSir"
