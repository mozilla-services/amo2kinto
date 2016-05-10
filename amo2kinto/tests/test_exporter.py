import mock
import unittest
from lxml import etree
from six import StringIO

from amo2kinto import constants, exporter, compare

ADDONS_DATA = {
    "id": "e3e8f123-588d-0f73-63d8-93bdfc6ae8e2",
    "last_modified": "1368430987148",
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


def test_addon_record():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_addons_items(xml_tree, [ADDONS_DATA],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
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
""".decode('utf-8')


def test_addon_record_with_no_version_range_info():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = ADDONS_DATA.copy()
    data['versionRange'] = []

    exporter.write_addons_items(xml_tree, [data],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <emItems>
    <emItem blockID="i454" id="sqlmoz@facebook.com">
      <prefs>
        <pref>test.blocklist</pref>
      </prefs>
    </emItem>
  </emItems>
</blocklist>
""".decode('utf-8')


def test_addon_record_with_no_targetApplication_info():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = ADDONS_DATA.copy()
    data['name'] = "Mozilla Service Pack (malware)"
    data['os'] = "WINNT"
    data['versionRange'] = [{
        "targetApplication": [],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 0
    }]

    exporter.write_addons_items(xml_tree, [data],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <emItems>
    <emItem blockID="i454" name="Mozilla Service Pack (malware)" \
os="WINNT" id="sqlmoz@facebook.com">
      <prefs>
        <pref>test.blocklist</pref>
      </prefs>
      <versionRange minVersion="0" maxVersion="*"/>
    </emItem>
  </emItems>
</blocklist>
""".decode('utf-8')


def test_addon_record_with_no_targetApplication_matching():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = ADDONS_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [
            {"guid": "{some-other-application}",
             "minVersion": "1.2",
             "maxVersion": "1.4"}
        ],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 3
    }]

    exporter.write_addons_items(xml_tree, [data],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <emItems/>
</blocklist>
""".decode('utf-8')


PLUGIN_DATA = {
    "id": "6a1b6dfe-f463-3061-e8f8-6e896ccf2a8a",
    "last_modified": "1301581706645",
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


def test_between_does_not_fails_with_none():
    assert exporter.between(compare.version_int("46.2"), None, None)


def test_plugin_record():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_plugin_items(xml_tree, [PLUGIN_DATA],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange maxVersion="4.1.10328.0" minVersion="0" severity="0" \
vulnerabilitystatus="1">
        <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
          <versionRange maxVersion="3.*" minVersion="3.0a1"/>
        </targetApplication>
      </versionRange>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    exporter.write_plugin_items(xml_tree, [PLUGIN_DATA],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange maxVersion="4.1.10328.0" minVersion="0" severity="0" \
vulnerabilitystatus="1"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_no_guid():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 0,
        "vulnerabilityStatus": "1"
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange severity="0" vulnerabilitystatus="1"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_no_guid_and_no_vulnerability():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 1
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_no_guid_and_severity_only():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [],
        "severity": 1
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange severity="1"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_no_guid_and_severity_0():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [],
        "severity": 0
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange severity="0"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_guid_and_no_min_max_version():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [
            {"guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
             "minVersion": "3.6",
             "maxVersion": "3.6.*"}
        ],
        "severity": 0,
        "vulnerabilityStatus": 1
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange severity="0" vulnerabilitystatus="1"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_guid_and_empty_versionRange():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [
            {"guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
             "minVersion": "3.6",
             "maxVersion": "3.6.*"}
        ]
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_api_version_2_with_related_version():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [
            {"guid": "{ec8030f7-c20a-464f-9b0e-13a3a9e97384}",
             "minVersion": "3.6",
             "maxVersion": "3.6.*"}
        ],
        "severity": 0,
        "vulnerabilityStatus": 1
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID,
                                api_ver=2, app_ver="3.6.1")

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange severity="0" vulnerabilitystatus="1"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_no_targetApplication_info():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['name'] = "Yahoo Application State Plugin"
    data['os'] = "WINNT"
    data['xpcomabi'] = "test"
    data['versionRange'] = [{
        "targetApplication": [],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 0,
        "vulnerabilityStatus": "1"
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems>
    <pluginItem blockID="p26" name="Yahoo Application State Plugin" os="WINNT"\
 xpcomabi="test">
      <match exp="^Yahoo Application State Plugin$" name="name"/>
      <match exp="npYState.dll" name="filename"/>
      <match exp="^Yahoo Application State Plugin$" name="description"/>
      <infoURL>https://get.adobe.com/flashplayer/</infoURL>
      <versionRange maxVersion="*" minVersion="0" severity="0" \
vulnerabilitystatus="1"/>
    </pluginItem>
  </pluginItems>
</blocklist>
""".decode('utf-8')


def test_plugin_record_with_no_targetApplication_matching():
    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='1459262434336'
    )

    data = PLUGIN_DATA.copy()
    data['versionRange'] = [{
        "targetApplication": [
            {"guid": "{some-other-application}",
             "minVersion": "1.2",
             "maxVersion": "1.4"}
        ],
        "minVersion": "0",
        "maxVersion": "*",
        "severity": 3
    }]

    exporter.write_plugin_items(xml_tree, [data],
                                constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <pluginItems/>
</blocklist>
""".decode('utf-8')


GFX_DATA = {
    "id": "00a6b9d2-285f-83f0-0a1f-ef0205a60067",
    "last_modified": "1348467813852",
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

    exporter.write_gfx_items(xml_tree, [GFX_DATA],
                             constants.FIREFOX_APPID)

    result = etree.tostring(
        etree.ElementTree(xml_tree),
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <gfxItems>
    <gfxBlacklistEntry blockID="g35">
      <os>WINNT 6.1</os>
      <vendor>0x10de</vendor>
      <feature>DIRECT2D</feature>
      <featureStatus>BLOCKED_DRIVER_VERSION</featureStatus>
      <driverVersion>8.17.12.5896</driverVersion>
      <driverVersionComparator>LESS_THAN_OR_EQUAL</driverVersionComparator>
      <devices>
        <device>0x0a6c</device>
      </devices>
    </gfxBlacklistEntry>
  </gfxItems>
</blocklist>
""".decode('utf-8')


CERTIFICATE_DATA = {
    "id": "fe7681eb-8480-718e-9870-084dca698f1d",
    "last_modified": "1448372434324",
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
        encoding='UTF-8').decode('utf-8')

    assert result == b"""<?xml version='1.0' encoding='UTF-8'?>
<blocklist lastupdate="1459262434336" \
xmlns="http://www.mozilla.org/2006/addons-blocklist">
  <certItems>
    <certItem issuerName="MBQxEjAQBgNVBAMTCWVEZWxsUm9vdA==">
      <serialNumber>a8V7lRiTqpdLYkrAiPw7tg==</serialNumber>
    </certItem>
  </certItems>
</blocklist>
""".decode('utf-8')


class TestMain(unittest.TestCase):
    def setUp(self):
        p = mock.patch('kinto_client.cli_utils.Client')
        self.MockedClient = p.start()
        self.MockedClient.return_value.get_records.return_value = []
        self.addCleanup(p.stop)

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
            'enabled': True,
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(**cert_arguments)

        gfx_arguments = {
            'bucket': kwargs['gfx_bucket'],
            'collection': kwargs['gfx_collection'],
            'enabled': True,
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(**gfx_arguments)

        addons_arguments = {
            'bucket': kwargs['addons_bucket'],
            'collection': kwargs['addons_collection'],
            'enabled': True,
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(
            **addons_arguments)

        plugins_arguments = {
            'bucket': kwargs['plugins_bucket'],
            'collection': kwargs['plugins_collection'],
            'enabled': True,
            '_sort': 'last_modified',
        }

        kinto_client.return_value.get_records.assert_any_call(
            **plugins_arguments)

    def test_main_default(self):
        # let's check that main() parsing uses our defaults
        exporter.main([])
        self.assert_arguments(self.MockedClient)

    def test_main_custom_server(self):
        exporter.main(['-s', 'http://yeah'])
        self.assert_arguments(self.MockedClient, kinto_server='http://yeah')

    def test_can_define_the_certificates_bucket_and_collection(self):
        exporter.main(['--certificates-bucket', 'bucket',
                       '--certificates-collection', 'collection'])
        self.assert_arguments(self.MockedClient,
                              certificates_bucket='bucket',
                              certificates_collection='collection')

    def test_can_define_the_gfx_bucket_and_collection(self):
        exporter.main(['--gfx-bucket', 'bucket',
                       '--gfx-collection', 'collection'])
        self.assert_arguments(self.MockedClient,
                              gfx_bucket='bucket',
                              gfx_collection='collection')

    def test_can_define_the_addons_bucket_and_collection(self):
        exporter.main(['--addons-bucket', 'bucket',
                       '--addons-collection', 'collection'])
        self.assert_arguments(self.MockedClient,
                              addons_bucket='bucket',
                              addons_collection='collection')

    def test_can_define_the_plugins_bucket_and_collection(self):
        exporter.main(['--plugins-bucket', 'bucket',
                       '--plugins-collection', 'collection'])
        self.assert_arguments(self.MockedClient,
                              plugins_bucket='bucket',
                              plugins_collection='collection')

    def test_can_define_the_auth_credentials(self):
        exporter.main(['--auth', 'user:pass'])
        self.assert_arguments(self.MockedClient, auth=('user', 'pass'))

    def test_can_define_the_output_file(self):
        out_file = StringIO()
        with mock.patch.object(out_file, 'close') as mocked_close:
            with mock.patch('amo2kinto.exporter.open', return_value=out_file):
                exporter.main(['--out', 'file'])
                self.assert_arguments(self.MockedClient)

                self.assertTrue(mocked_close.called)
                self.assertNotEqual(len(out_file.getvalue()), 0)

    def test_get_records_read_fails(self):
        with mock.patch('kinto_client.cli_utils.Client') as MockedClient:
            MockedClient.return_value.get_records.side_effect = Exception
            with mock.patch('amo2kinto.exporter.logger') as mocked_logger:
                exporter.main([])
                self.assertEqual(mocked_logger.warn.call_count, 4)

    def test_last_updated_uses_greater_value(self):
        self.MockedClient.return_value.get_records.side_effect = (
            [ADDONS_DATA], [PLUGIN_DATA], [GFX_DATA], [CERTIFICATE_DATA]
        )
        out_file = StringIO()
        with mock.patch.object(out_file, 'close'):
            with mock.patch('amo2kinto.exporter.open', return_value=out_file):
                exporter.main(['--out', 'file'])
        self.assertIn('lastupdate="1448372434324"', out_file.getvalue())
