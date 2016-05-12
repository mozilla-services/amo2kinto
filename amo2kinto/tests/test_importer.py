import codecs
import json
import mock
import os
import pytest
import unittest

from jsonschema.exceptions import ValidationError

from amo2kinto import constants
from amo2kinto.importer import FIELDS, prepare_amo_records, sync_records, main

ADDONS_DATA = {
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
            {"guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
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
        "targetApplication": [],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 3
    }],
    "prefs": ["test.blocklist"]
}


def test_addon_record():
    assert prepare_amo_records([ADDONS_DATA], FIELDS['addons']) == [{
        "id": "e3e8f123-588d-0f73-63d8-93bdfc6ae8e2",
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
            'targetApplication': [
                {'guid': '{ec8030f7-c20a-464f-9b0e-13a3a9e97384}',
                 'minVersion': '3.6',
                 'maxVersion': '3.6.*'},
                {'guid': '{some-other-application}',
                 'minVersion': '1.2',
                 'maxVersion': '1.4'}
            ],
            "minVersion": "0",
            "maxVersion": "*",
            "severity": 3
        }, {
            "targetApplication": [],
            "minVersion": "0",
            "maxVersion": "*",
            "severity": 3
        }],
        "prefs": ["test.blocklist"]
    }]


PLUGIN_DATA = {
    "blockID": "p26",
    "matchName": "^Yahoo Application State Plugin$",
    "matchFilename": "npYState.dll",
    "matchDescription": "^Yahoo Application State Plugin$",
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
            "guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
            "maxVersion": "3.*"
        }]
    }]
}


def test_plugin_record():
    assert prepare_amo_records([PLUGIN_DATA], FIELDS['plugins']) == [{
        "id": "6a1b6dfe-f463-3061-e8f8-6e896ccf2a8a",
        "blockID": "p26",
        "matchName": "^Yahoo Application State Plugin$",
        "matchFilename": "npYState.dll",
        "matchDescription": "^Yahoo Application State Plugin$",
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
                "guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
                "maxVersion": "3.*"
            }]
        }]
    }]


GFX_DATA = {
    "blockID": "g35",
    "devices": ["0x0a6c"],
    "driverVersion": "8.17.12.5896",
    "driverVersionComparator": "LESS_THAN_OR_EQUAL",
    "feature": "DIRECT2D",
    "featureStatus": "BLOCKED_DRIVER_VERSION",
    "vendor": "0x10de",
    "details": {
        "who": "All Firefox users who have these drivers installed.",
        "created": "2012-09-24T08:23:33Z",
        "name": "ATI/AMD driver 8.982.0.0",
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=792480",
        "why": "Some features in these drivers are causing frequent crashes "
        "in Firefox."
    },
    "os": "WINNT 6.1"
}


def test_gfx_record():
    assert prepare_amo_records([GFX_DATA], FIELDS['gfx']) == [{
        "id": "00a6b9d2-285f-83f0-0a1f-ef0205a60067",
        "blockID": "g35",
        "devices": ["0x0a6c"],
        "driverVersion": "8.17.12.5896",
        "driverVersionComparator": "LESS_THAN_OR_EQUAL",
        "feature": "DIRECT2D",
        "featureStatus": "BLOCKED_DRIVER_VERSION",
        "vendor": "0x10de",
        "details": {
            "who": "All Firefox users who have these drivers installed.",
            "created": "2012-09-24T08:23:33Z",
            "name": "ATI/AMD driver 8.982.0.0",
            "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=792480",
            "why": "Some features in these drivers are causing frequent "
            "crashes in Firefox."
        },
        "os": "WINNT 6.1"
    }]


CERTIFICATE_DATA = {
    "blockID": "c796",
    "issuerName": "MBQxEjAQBgNVBAMTCWVEZWxsUm9vdA==",
    "serialNumber": "a8V7lRiTqpdLYkrAiPw7tg==",
    "details": {
        "who": ".",
        "created": "2015-11-24T14:40:34Z",
        "name": "eDellRoot",
        "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1227729",
        "why": "."
    }
}


def test_certificate_record():
    assert prepare_amo_records([CERTIFICATE_DATA], FIELDS['certificates']) == [
        {'id': 'fe7681eb-8480-718e-9870-084dca698f1d',
         'issuerName': 'MBQxEjAQBgNVBAMTCWVEZWxsUm9vdA==',
         'serialNumber': 'a8V7lRiTqpdLYkrAiPw7tg==',
         "details": {
             "who": ".",
             "created": "2015-11-24T14:40:34Z",
             "name": "eDellRoot",
             "bug": "https://bugzilla.mozilla.org/show_bug.cgi?id=1227729",
             "why": "."}}]


def test_sync_records_calls_the_scenario():
    prepared_records = []
    with mock.patch(
            'amo2kinto.importer.get_kinto_records',
            return_value=mock.sentinel.kinto_records) as get_kinto_records:
        with mock.patch(
                'amo2kinto.importer.prepare_amo_records',
                return_value=prepared_records) as p_amo_records:
            with mock.patch(
                    'amo2kinto.importer.get_diff',
                    return_value=(
                        mock.sentinel.to_create,
                        mock.sentinel.to_delete)) as get_diff:
                with mock.patch(
                        'amo2kinto.importer.push_changes') as push_changes:

                    amo_records = []

                    sync_records(amo_records,
                                 mock.sentinel.fields,
                                 mock.sentinel.kinto_client,
                                 mock.sentinel.bucket,
                                 mock.sentinel.collection,
                                 mock.sentinel.schema,
                                 mock.sentinel.permissions)

                    p_amo_records.assert_called_with(
                        amo_records,
                        mock.sentinel.fields)

                    get_kinto_records.assert_called_with(
                        kinto_client=mock.sentinel.kinto_client,
                        bucket=mock.sentinel.bucket,
                        collection=mock.sentinel.collection,
                        schema=mock.sentinel.schema,
                        permissions=mock.sentinel.permissions)

                    get_diff.assert_called_with(
                        prepared_records,
                        mock.sentinel.kinto_records)

                    push_changes.assert_called_with(
                        (mock.sentinel.to_create, mock.sentinel.to_delete),
                        mock.sentinel.kinto_client,
                        bucket=mock.sentinel.bucket,
                        collection=mock.sentinel.collection)


SCHEMAS = {
    'certificates': None,
    'gfx': None,
    'addons': None,
    'plugins': None,
}


with codecs.open(constants.SCHEMA_FILE, encoding='utf-8') as f:
    SCHEMAS = json.load(f)['collections']


RECORDS = {
    'certificates': None,
    'gfx': None,
    'addons': None,
    'plugins': None,
}

RECORDS_FILE = os.path.join(os.path.dirname(__file__),
                            'fixtures', 'blocklists.json')
with codecs.open(RECORDS_FILE, encoding='utf-8') as f:
    RECORDS = json.load(f)


class TestSyncRecords(unittest.TestCase):
    def setUp(self):
        p = mock.patch('amo2kinto.importer.get_kinto_records', return_value=[])
        self.addCleanup(p.stop)
        p.start()
        p = mock.patch('amo2kinto.importer.push_changes')
        self.addCleanup(p.stop)
        p.start()

    def test_sync_records_validate_records_against_schema(self):
        # sync_records should not raise an Exception here.
        sync_records(RECORDS['addons'],
                     FIELDS['addons'],
                     mock.sentinel.kinto_client,
                     mock.sentinel.bucket,
                     mock.sentinel.collection,
                     SCHEMAS['addons'],
                     mock.sentinel.permissions)

    def test_sync_records_fails_if_the_schema_does_not_validate_records(self):
        # Make sure it raises an exception with wrong records.
        with pytest.raises(ValidationError):
            sync_records(RECORDS['gfx'],
                         FIELDS['gfx'],
                         mock.sentinel.kinto_client,
                         mock.sentinel.bucket,
                         mock.sentinel.collection,
                         SCHEMAS['addons']['config']['schema'],
                         mock.sentinel.permissions)


class TestMain(unittest.TestCase):
    def setUp(self):
        # Mock requests
        request_mock = mock.MagicMock()
        request_mock.json.return_value = RECORDS
        p = mock.patch('requests.get', return_value=request_mock)
        self.addCleanup(p.stop)
        p.start()

        # Mock client
        self.MockedClient = mock.MagicMock()
        self.MockedClient.return_value.session.request.return_value = {
            'capabilities': {}
        }, {}
        p = mock.patch('kinto_client.cli_utils.Client', self.MockedClient)
        self.addCleanup(p.stop)
        p.start()

    def assert_arguments(self, mock_sync, kinto_client, **kwargs):
        kwargs.setdefault('kinto_server', constants.KINTO_SERVER)
        kwargs.setdefault('auth', constants.AUTH)
        kwargs.setdefault('certificates_bucket', constants.CERT_BUCKET)
        kwargs.setdefault('certificates_collection', constants.CERT_COLLECTION)
        kwargs.setdefault('gfx_bucket', constants.GFX_BUCKET)
        kwargs.setdefault('gfx_collection', constants.GFX_COLLECTION)
        kwargs.setdefault('addons_bucket', constants.ADDONS_BUCKET)
        kwargs.setdefault('addons_collection', constants.ADDONS_COLLECTION)
        kwargs.setdefault('plugins_bucket', constants.PLUGINS_BUCKET)
        kwargs.setdefault('plugins_collection', constants.PLUGINS_COLLECTION)
        kwargs.setdefault('no_schema', False)
        kwargs.setdefault('amo_server', constants.ADDONS_SERVER)
        kwargs.setdefault('schemas', SCHEMAS)

        kinto_client.assert_called_with(server_url=kwargs['kinto_server'],
                                        auth=kwargs['auth'],
                                        bucket=None,
                                        collection=None)

        cert_schema = kwargs['schemas']['certificates']['config']['schema']
        gfx_schema = kwargs['schemas']['gfx']['config']['schema']
        addons_schema = kwargs['schemas']['addons']['config']['schema']
        plugins_schema = kwargs['schemas']['plugins']['config']['schema']

        if kwargs['no_schema']:
            cert_schema = None
            gfx_schema = None
            addons_schema = None
            plugins_schema = None

        cert_arguments = {
            'amo_records': RECORDS['certificates'],
            'fields': FIELDS['certificates'],
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['certificates_bucket'],
            'collection': kwargs['certificates_collection'],
            'schema': cert_schema,
            'permissions': constants.COLLECTION_PERMISSIONS,
        }

        mock_sync.assert_any_call(**cert_arguments)

        gfx_arguments = {
            'amo_records': RECORDS['gfx'],
            'fields': FIELDS['gfx'],
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['gfx_bucket'],
            'collection': kwargs['gfx_collection'],
            'schema': gfx_schema,
            'permissions': constants.COLLECTION_PERMISSIONS,
        }

        mock_sync.assert_any_call(**gfx_arguments)

        addons_arguments = {
            'amo_records': RECORDS['addons'],
            'fields': FIELDS['addons'],
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['addons_bucket'],
            'collection': kwargs['addons_collection'],
            'schema': addons_schema,
            'permissions': constants.COLLECTION_PERMISSIONS,
        }

        mock_sync.assert_any_call(**addons_arguments)

        plugins_arguments = {
            'amo_records': RECORDS['plugins'],
            'fields': FIELDS['plugins'],
            'kinto_client': kinto_client.return_value,
            'bucket': kwargs['plugins_bucket'],
            'collection': kwargs['plugins_collection'],
            'schema': plugins_schema,
            'permissions': constants.COLLECTION_PERMISSIONS,
        }

        mock_sync.assert_any_call(**plugins_arguments)

    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main([])

        self.assert_arguments(mock_sync, self.MockedClient)

    def test_warning_on_server_schema_capability_missing(self):
        with mock.patch('amo2kinto.importer.sync_records'):
            with mock.patch('amo2kinto.importer.logger') as mocked_logger:
                # capabilities is mocked to an empty value dict in the setUp.
                main([])

        self.assertEqual(mocked_logger.warn.call_count, 2)

    def test_no_warning_on_server_schema_capability_enabled(self):
        with mock.patch('amo2kinto.importer.sync_records'):
            with mock.patch('amo2kinto.importer.logger') as mocked_logger:
                self.MockedClient.return_value.session.request.return_value = {
                    'capabilities': {"schema": {}}
                }, {}
                main([])

        self.assertEqual(mocked_logger.warn.call_count, 0)

    def test_no_schema_option_does_add_the_schema(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(['--no-schema'])

        self.assert_arguments(mock_sync, self.MockedClient,
                              no_schema=True)

    def test_main_custom_server(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(['-s', 'http://yeah'])

        self.assert_arguments(mock_sync, self.MockedClient,
                              kinto_server='http://yeah')

    def test_can_define_the_certificates_bucket_and_collection(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(['--certificates-bucket', 'bucket',
                  '--certificates-collection', 'collection'])

        self.assert_arguments(mock_sync, self.MockedClient,
                              certificates_bucket='bucket',
                              certificates_collection='collection')

    def test_can_define_the_gfx_bucket_and_collection(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(
                ['--gfx-bucket', 'bucket',
                 '--gfx-collection', 'collection'])
        self.assert_arguments(mock_sync, self.MockedClient,
                              gfx_bucket='bucket',
                              gfx_collection='collection')

    def test_can_define_the_addons_bucket_and_collection(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(
                ['--addons-bucket', 'bucket',
                 '--addons-collection', 'collection'])
        self.assert_arguments(mock_sync, self.MockedClient,
                              addons_bucket='bucket',
                              addons_collection='collection')

    def test_can_define_the_plugins_bucket_and_collection(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(
                ['--plugins-bucket', 'bucket',
                 '--plugins-collection', 'collection'])
        self.assert_arguments(mock_sync, self.MockedClient,
                              plugins_bucket='bucket',
                              plugins_collection='collection')

    def test_can_define_the_auth_credentials(self):
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(['--auth', 'user:pass'])

        self.assert_arguments(mock_sync, self.MockedClient,
                              auth=('user', 'pass'))

    def test_no_collections_means_all_collections(self):
        """If no 'collection' is passed as parameter, import all of them."""
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main([])

        # Nothing specific to be tested here, it's the default behavior
        self.assert_arguments(mock_sync, self.MockedClient)

    def test_only_import_certificats(self):
        """If only one collection is specified, only import it."""
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(['--certificates', '--no-schema'])

        mock_sync.assert_called_once_with(
            amo_records=RECORDS['certificates'],
            fields=FIELDS['certificates'],
            kinto_client=mock.ANY,
            bucket=constants.CERT_BUCKET,
            collection=constants.CERT_COLLECTION,
            schema=None,
            permissions=constants.COLLECTION_PERMISSIONS)

    def test_only_import_certs_and_gfx(self):
        """Only import specified collections"""
        with mock.patch('amo2kinto.importer.sync_records') as mock_sync:
            main(['--certificates', '-G', '--no-schema'])

        assert mock_sync.call_count == 2  # Only called for certificats and gfx
        mock_sync.assert_has_calls([
            mock.call(
                amo_records=RECORDS['certificates'],
                fields=FIELDS['certificates'],
                kinto_client=mock.ANY,
                bucket=constants.CERT_BUCKET,
                collection=constants.CERT_COLLECTION,
                schema=None,
                permissions=constants.COLLECTION_PERMISSIONS),
            mock.call(
                amo_records=RECORDS['gfx'],
                fields=FIELDS['gfx'],
                kinto_client=mock.ANY,
                bucket=constants.GFX_BUCKET,
                collection=constants.GFX_COLLECTION,
                schema=None,
                permissions=constants.COLLECTION_PERMISSIONS)],
            any_order=True)
