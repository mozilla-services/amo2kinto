import json
import mock
import os
from six import StringIO

from amo2kinto.verifier import sort_lists_in_dict, main


def build_path(filename):
    return os.path.join(os.path.dirname(__file__), 'fixtures', filename)


def test_sort_lists_in_dict_handles_recursion():
    assert json.dumps(sort_lists_in_dict({
        '@name': 'judith',
        'validators': [{
            '@id': 'gbc',
            'toto': ['b', 'a']
        }, {
            '@id': 'abc',
            'toto': ['c', 'd', 'a'],
            'apps': [{
                '@guid': 'cde',
                'minVersion': 2,
            }, {
                '@guid': 'abc',
                'minVersion': 3
            }]
        }]
    }), sort_keys=True) == (
        '{"@name": "judith", "validators": [{'
        '"@id": "abc", '
        '"apps": [{"@guid": "abc", "minVersion": 3}, '
        '{"@guid": "cde", "minVersion": 2}], '
        '"toto": ["a", "c", "d"]}, '
        '{"@id": "gbc", "toto": ["a", "b"]}]}'
    )


def test_files_checking():
    with mock.patch('sys.stdout', new_callable=StringIO) as stdout:
        with mock.patch('sys.stderr', new_callable=StringIO) as stderr:
            main([build_path('blocklist.xml'),
                  build_path('generated-blocklist.xml')])

        assert stdout.getvalue() == ''
        assert stderr.getvalue() == ''


def test_fails_if_file_does_not_exists():
    assert main(['unknown']) == 1


def test_verifier_supports_http_links():
    with open(build_path('blocklist.xml')) as f:
        blocklist_content = f.read()

    response = mock.MagicMock(text=blocklist_content)
    with mock.patch('requests.get', return_value=response) as mocked_request:
        main(['http://first_server/url/', 'http://second_server/url/'])

        mocked_request.assert_any_call('http://first_server/url/')
        mocked_request.assert_any_call('http://second_server/url/')


def test_clean_option_does_not_remove_tmp_files():
    with mock.patch('sys.stderr', new_callable=StringIO) as stderr:
        main([build_path('blocklist.xml'),
              build_path('generated-blocklist.xml'), '-k'])

        content = stderr.getvalue()
        assert content.startswith('$ diff -U10 -u'), content


def test_in_case_diff_fails_display_the_error():
    with mock.patch('sys.stderr', new_callable=StringIO) as stderr:
        main([build_path('fennec-blocklist.xml'),
              build_path('generated-blocklist.xml')])

        assert stderr.getvalue() != ''


def test_in_case_diff_fails_exit_with_2():
    with mock.patch('sys.stderr', new_callable=StringIO):
        assert main([build_path('fennec-blocklist.xml'),
                     build_path('generated-blocklist.xml')]) == 2
