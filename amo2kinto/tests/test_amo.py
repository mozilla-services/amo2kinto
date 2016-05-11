from amo2kinto.amo import make_id_from_string, prepare_amo_records


def test_make_id_from_string():
    """It should handle strings, list, int and dict."""
    assert make_id_from_string("foo") == 'acbd18db-4cc2-f85c-edef-654fccc4a4d8'


def test_prepare_amo_records():
    """It should handle strings, list, int, boolean and dict."""
    fields = ['foo', 'bar']
    records = [{
        'blockID': 'c1',
        'foo': 'toto',
        'bar': 'tata',
        'unknown': 'ignore'
    }, {
        'blockID': 'c2',
        'foo': 'taratata',
        'bar': 'foobar',
    }]

    assert prepare_amo_records(records, fields) == [{
        'id': 'a9f7e979-65d6-cf79-9a52-9102a973b8b9',
        'foo': 'toto',
        'bar': 'tata',
    }, {
        'id': '9ab62b5e-f34a-9854-38bf-df7ee0102229',
        'foo': 'taratata',
        'bar': 'foobar',
    }]
