import mock
import unittest

from jinja2 import Template

from amo2kinto import constants
from amo2kinto.generator import (
    iso2human, get_template, generate, generate_index, generate_record, get_record_filename, main)


ADDONS_DATA = {
    "id": "e3e8f123-588d-0f73-63d8-93bdfc6ae8e2",
    "last_modified": 1368430987148,
    "guid": "sqlmoz@facebook.com",
    "blockID": "i454",
    "details": {
        "who": "All Firefox users who have this extension installed.",
        "created": "2013-05-13T09:43:07Z",
        "name": "Mozilla Service Pack (malware)",
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=871610",
        "why": "This extension is malware posing as Mozilla software. "
        "It hijacks Facebook accounts and spams other Facebook users."
    },
    "versionRange": [{
        "targetApplication": [
            {"guid": constants.FIREFOX_APPID,
             "minVersion": "3.6",
             "maxVersion": "3.6.*"},
            {"guid": "{some-other-application}",
             "minVersion": "1.2",
             "maxVersion": "1.4"}
        ],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 3
    }, {
        "targetApplication": [
            {"guid": "{some-other-application}",
             "minVersion": "1.2",
             "maxVersion": "1.4"}
        ],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 3
    }, {
        "targetApplication": [],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 0
    }],
    "prefs": ["test.blocklist"]
}


PLUGIN_DATA = {
    "id": "6a1b6dfe-f463-3061-e8f8-6e896ccf2a8a",
    "last_modified": 1301581706645,
    "blockID": "p26",
    "matchName": "^Yahoo Application State Plugin$",
    "matchFilename": "npYState.dll",
    "matchDescription": "^Yahoo Application State Plugin$",
    "infoURL": "https://get.adobe.com/flashplayer/",
    "details": {
        "who": "Users of all versions of Yahoo Application State Plugin "
        "for Firefox 3 and later.\r\n\r\nUsers of all versions of Yahoo "
        "Application State Plugin for SeaMonkey 1.0.0.5 and later.",
        "created": "2011-03-31T16:28:26Z",
        "name": "Yahoo Application State Plugin",
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=421993",
        "why": "This plugin causes a high volume of Firefox and SeaMonkey "
        "crashes."
    },
    "versionRange": [{
        "minVersion": "0",
        "maxVersion": "4.1.10328.0",
        "severity": 0,
        "vulnerabilityStatus": 1,
        "targetApplication": [{
            "minVersion": "3.0a1",
            "guid": constants.FIREFOX_APPID,
            "maxVersion": "3.*"
        }]
    }]
}


def test_iso2human():
    assert iso2human(ADDONS_DATA['details']['created']) == 'May 13, 2013'
    assert iso2human(PLUGIN_DATA['details']['created']) == 'Mar 31, 2011'


def test_get_template():
    assert isinstance(get_template('collection.tpl'), Template)
    assert isinstance(get_template('record.tpl'), Template)


def test_generate_index():
    records = [ADDONS_DATA, PLUGIN_DATA]
    template = get_template('collection.tpl')
    f = mock.mock_open()
    with mock.patch('amo2kinto.generator.open', f, create=True):
        generate_index(records, template, 'tmp')
        f.assert_called_once_with('tmp/index.html', 'w')
        handle = f()
        assert handle.write.call_count == 1


def test_get_record_filename_uses_blockID():
    record_id = '9cff5990-47fe-4732-afaa-d2d82094baa1'
    assert get_record_filename({'blockID': 'i454', 'id': record_id}) == 'i454.html'


def test_get_record_filename_uses_record_id():
    record_id = '9cff5990-47fe-4732-afaa-d2d82094baa1'
    assert get_record_filename({'id': record_id}) == '%s.html' % record_id


def test_generate_record():
    template = get_template('record.tpl')
    f = mock.mock_open()
    with mock.patch('amo2kinto.generator.os.makedirs'):
        with mock.patch('amo2kinto.generator.open', f, create=True):
            generate_record(ADDONS_DATA, template, 'tmp', get_record_filename)
            f.assert_called_once_with('tmp/i454.html', 'w')
            handle = f()
            assert handle.write.call_count == 1


def test_generate_grabs_addons_and_plugins_records():
    kinto_client = mock.MagicMock()
    kinto_client.get_records.side_effect = [[ADDONS_DATA], [PLUGIN_DATA]]
    collections = ['/buckets/blocklists/collections/addons',
                   '/buckets/blocklists/collections/plugins']

    collection_template = get_template('collection.tpl')
    record_template = get_template('record.tpl')

    with mock.patch('amo2kinto.generator.os.makedirs') as mocked_makedirs:
        with mock.patch('amo2kinto.generator.get_template',
                        side_effect=[collection_template, record_template]):
            with mock.patch('amo2kinto.generator.generate_index') as gi:
                with mock.patch('amo2kinto.generator.generate_record') as gr:
                    generate(kinto_client, collections, 'tmp', 'collection.tpl', 'record.tpl')

                    assert gi.call_count == 1
                    gi.assert_called_with([ADDONS_DATA, PLUGIN_DATA], collection_template, 'tmp')

                    assert gr.call_count == 2
                    gr.assert_any_call(ADDONS_DATA, record_template, 'tmp', get_record_filename)
                    gr.assert_any_call(PLUGIN_DATA, record_template, 'tmp', get_record_filename)

                    mocked_makedirs.assert_called_with('tmp')


def test_generate_uses_last_modified_if_created_is_missing():
    kinto_client = mock.MagicMock()
    data = ADDONS_DATA.copy()
    del data['details']['created']
    kinto_client.get_records.return_value = [data]
    collections = ['/buckets/blocklists/collections/addons']

    with mock.patch('amo2kinto.generator.os.makedirs'):
        f = mock.mock_open()
        with mock.patch('amo2kinto.generator.open', f, create=True):
            generate(kinto_client, collections, 'tmp', 'collection.tpl', 'record.tpl')

            assert f.return_value.write.call_count == 2

            # Present in index
            assert b'May 13, 2013' in f.return_value.write.call_args_list[0][0][0]

            # Present in the record file
            assert b'May 13, 2013' in f.return_value.write.call_args_list[1][0][0]


class TestMain(unittest.TestCase):
    def setUp(self):
        p = mock.patch('kinto_http.cli_utils.Client')
        self.MockedClient = p.start()
        self.MockedClient.return_value.get_records.return_value = []
        self.addCleanup(p.stop)

        p = mock.patch('amo2kinto.generator.os.makedirs')
        self.mocked_makedirs = p.start()
        self.addCleanup(p.stop)

        p = mock.patch('amo2kinto.generator.open', create=True)
        self.mocked_open = p.start()
        self.addCleanup(p.stop)

    def assert_arguments(self, kinto_client, **kwargs):
        kwargs.setdefault('kinto_server', constants.KINTO_SERVER)
        kwargs.setdefault('auth', constants.AUTH)
        kwargs.setdefault('bucket', constants.DESTINATION_BUCKET)
        kwargs.setdefault('addons_collection', constants.ADDONS_COLLECTION)
        kwargs.setdefault('plugins_collection', constants.PLUGINS_COLLECTION)
        kwargs.setdefault('target_dir', constants.TARGET_DIR)

        kinto_client.assert_called_with(server_url=kwargs['kinto_server'],
                                        auth=kwargs['auth'],
                                        bucket=kwargs['bucket'],
                                        collection=None)

        addons_arguments = {
            'bucket': kwargs['bucket'],
            'collection': kwargs['addons_collection'],
        }
        kinto_client.return_value.get_records.assert_any_call(
            **addons_arguments)

        plugins_arguments = {
            'bucket': kwargs['bucket'],
            'collection': kwargs['plugins_collection'],
        }

        kinto_client.return_value.get_records.assert_any_call(
            **plugins_arguments)

    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        main([])
        self.assert_arguments(self.MockedClient)

    def test_main_custom_server(self):
        main(['-s', 'http://yeah'])
        self.assert_arguments(self.MockedClient, kinto_server='http://yeah')

    def test_can_define_the_addons_collection(self):
        main(['--bucket', 'bucket',
              '--addons-collection', 'collection'])
        self.assert_arguments(self.MockedClient,
                              bucket='bucket',
                              addons_collection='collection')

    def test_can_define_the_plugins_collection(self):
        main(['--bucket', 'bucket',
              '--plugins-collection', 'collection'])
        self.assert_arguments(self.MockedClient,
                              bucket='bucket',
                              plugins_collection='collection')

    def test_can_define_the_auth_credentials(self):
        main(['--auth', 'user:pass'])
        self.assert_arguments(self.MockedClient, auth=('user', 'pass'))

    def test_can_define_the_output_directory(self):
        main(['--target-dir', 'file'])
        self.assert_arguments(self.MockedClient)

        self.mocked_open.assert_called_with('file/index.html', 'w')
