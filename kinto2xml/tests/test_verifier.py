import json
from kinto2xml.verifier import sort_lists_in_dict


def test_sort_lists_in_dict_handles_recursion():
    assert json.dumps(sort_lists_in_dict({
        'name': 'judith',
        'validators': [{
            'id': 'gbc',
            'toto': ['b', 'a']
        }, {
            'id': 'abc',
            'toto': ['c', 'd', 'a'],
            'apps': [{
                'guid': 'cde',
                'minVersion': 2,
            }, {
                'guid': 'abc',
                'minVersion': 3
            }]
        }]
    }), sort_keys=True) == (
        '{"name": "judith", "validators": ['
        '{"apps": [{"guid": "abc", "minVersion": 3}, '
        '{"guid": "cde", "minVersion": 2}], '
        '"id": "abc", '
        '"toto": ["a", "c", "d"]}, '
        '{"id": "gbc", "toto": ["a", "b"]}]}'
    )
