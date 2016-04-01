import mock
import unittest
from lxml import etree
from six import StringIO

from kinto2xml import constants, exporter

ADDONS_DATA = {
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
        "maxVersion": "*"
    }],
    "prefs": ["test.blocklist"]
}


def test_addon_record():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_addons_items(xml_tree, [ADDONS_DATA])

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8')

    assert result == """<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <emItems>
    <emItem blockID="i454" id="sqlmoz@facebook.com">
      <prefs>
        <pref>test.blocklist</pref>
      </prefs>
      <versionRange minVersion="0" maxVersion="*" severity="3">
        <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
          <versionRange maxVersion="3.6.*" minVersion="3.6"/>
        </targetApplication>
      </versionRange>
      <versionRange minVersion="0" maxVersion="*"/>
    </emItem>
  </emItems>
</blocklist>
"""

PLUGIN_DATA = {
    "id": "6a1b6dfe-f463-3061-e8f8-6e896ccf2a8a",
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
            "guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
            "maxVersion": "3.*"
        }]
    }]
}


def test_plugin_record():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_plugin_items(xml_tree, [PLUGIN_DATA])

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8')

    assert result == """<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginsItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange minVersion="0" maxVersion="4.1.10328.0" \
vulnerabilitystatus="1">
        <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
          <versionRange maxVersion="3.*" minVersion="3.0a1"/>
        </targetApplication>
      </versionRange>
    </pluginItem>
  </pluginsItems>
</blocklist>
"""

GFX_DATA = {
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
        "why": "Some features in these drivers are causing frequent crashes "
        "in Firefox."
    },
    "os": "WINNT 6.1"
}


def test_gfx_record():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_gfx_items(xml_tree, [GFX_DATA])

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8')

    assert result == """<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <gfxItems>
    <gfxBlacklistEntry blockID="g35">
      <os>WINNT 6.1</os>
      <vendor>0x10de</vendor>
      <devices>
        <device>0x0a6c</device>
      </devices>
      <feature>DIRECT2D</feature>
      <featureStatus>BLOCKED_DRIVER_VERSION</featureStatus>
      <driverVersion>8.17.12.5896</driverVersion>
      <driverVersionComparator>LESS_THAN_OR_EQUAL</driverVersionComparator>
    </gfxBlacklistEntry>
  </gfxItems>
</blocklist>
"""


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
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_cert_items(xml_tree, [CERTIFICATE_DATA])

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8')

    assert result == """<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <certItems>
    <certItem issuerName="MBQxEjAQBgNVBAMTCWVEZWxsUm9vdA==">
      <serialNumber>a8V7lRiTqpdLYkrAiPw7tg==</serialNumber>
    </certItem>
  </certItems>
</blocklist>
"""


class TestMain(unittest.TestCase):
    def assert_arguments(self, kinto_client, **kwargs):
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

        kinto_client.assert_called_with(server_url=kwargs['kinto_server'],
                                        auth=kwargs['auth'],
                                        bucket=None,
                                        collection=None)

        cert_arguments = {
            'bucket': kwargs['certificates_bucket'],
            'collection': kwargs['certificates_collection'],
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(**cert_arguments)

        gfx_arguments = {
            'bucket': kwargs['gfx_bucket'],
            'collection': kwargs['gfx_collection'],
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(**gfx_arguments)

        addons_arguments = {
            'bucket': kwargs['addons_bucket'],
            'collection': kwargs['addons_collection'],
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(
            **addons_arguments)

        plugins_arguments = {
            'bucket': kwargs['plugins_bucket'],
            'collection': kwargs['plugins_collection'],
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(
            **plugins_arguments)

    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main([])
            self.assert_arguments(MockedClient)

    def test_main_custom_server(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main(['-s', 'http://yeah'])
            self.assert_arguments(MockedClient, kinto_server='http://yeah')

    def test_can_define_the_certificates_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main(['--certificates-bucket', 'bucket',
                           '--certificates-collection', 'collection'])
            self.assert_arguments(MockedClient,
                                  certificates_bucket='bucket',
                                  certificates_collection='collection')

    def test_can_define_the_gfx_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main(['--gfx-bucket', 'bucket',
                           '--gfx-collection', 'collection'])
            self.assert_arguments(MockedClient,
                                  gfx_bucket='bucket',
                                  gfx_collection='collection')

    def test_can_define_the_addons_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main(['--addons-bucket', 'bucket',
                           '--addons-collection', 'collection'])
            self.assert_arguments(MockedClient,
                                  addons_bucket='bucket',
                                  addons_collection='collection')

    def test_can_define_the_plugins_bucket_and_collection(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main(['--plugins-bucket', 'bucket',
                           '--plugins-collection', 'collection'])
            self.assert_arguments(MockedClient,
                                  plugins_bucket='bucket',
                                  plugins_collection='collection')

    def test_can_define_the_auth_credentials(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            exporter.main(['--auth', 'user:pass'])
            self.assert_arguments(MockedClient, auth=('user', 'pass'))

    def test_can_define_the_output_file(self):
        out_file = StringIO()
        with mock.patch('kinto2xml.exporter.open', return_value=out_file):
            with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
                exporter.main(['--out', 'file'])
                self.assert_arguments(MockedClient)
        self.assertTrue(out_file.closed)
        self.assertEqual(len(out_file.buflist), 1)

    def test_get_records_read_fails(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            MockedClient.return_value.get_records.side_effect = Exception
            with mock.patch('kinto2xml.exporter.logger') as mocked_logger:
                exporter.main([])
                self.assertEqual(mocked_logger.warn.call_count, 4)
