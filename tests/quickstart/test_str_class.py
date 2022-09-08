class TestStringMethods:
    def test_upper(self):
        assert "foo".upper() == "FOO"

    def test_isupper(self):
        assert "FOO".isupper()
        assert not "Foo".isupper()

    def test_split(self):
        s = "hello world"
        assert s.split() == ["hello", "world"]
