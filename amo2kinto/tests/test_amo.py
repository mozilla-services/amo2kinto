from amo2kinto.amo import make_id_from_string


def test_make_id_from_string():
    """It should handle strings, list, int and dict."""
    assert make_id_from_string("foo") == 'acbd18db-4cc2-f85c-edef-654fccc4a4d8'
