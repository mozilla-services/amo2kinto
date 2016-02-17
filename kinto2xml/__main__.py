import logging
import sys
from lxml import etree
from kinto_client import cli_utils

logger = logging.getLogger("kinto2xml")


# XXX: We might want to move this to kinto_client.cli_utils.
def remove_action(parser, short, long):
    actions = filter(
        lambda x: x.option_strings == [short, long],
        parser._actions
    )
    if len(actions) == 1:
        parser._handle_conflict_resolve(None, [
            (short, actions[0])
        ])
        parser._handle_conflict_resolve(None, [
            (long, actions[0])
        ])


def write_addons_items(xml_tree, records):
    """Generate the addons blocklists.

    <emItem blockID="i372" id="5nc3QHFgcb@r06Ws9gvNNVRfH.com">
      <versionRange minVersion="0" maxVersion="*" severity="3">
        <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
          <versionRange minVersion="39.0a1" maxVersion="*"/>
        </targetApplication>
      </versionRange>
      <prefs>
        <pref>browser.startup.homepage</pref>
        <pref>browser.search.defaultenginename</pref>
      </prefs>
    </emItem>
    """
    emItems = etree.SubElement(xml_tree, 'emItems')
    for item in records:
        if item['enabled']:
            emItem = etree.SubElement(emItems, 'emItem',
                                      blockID=item.get('blockID'),
                                      id=item['addonId'])
            prefs = etree.SubElement(emItem, 'prefs')
            for p in item['prefs']:
                pref = etree.SubElement(prefs, 'pref')
                pref.text = p

            versionRange = etree.SubElement(
                emItem, 'versionRange',
                minVersion=version.get('minVersion'),
                maxVersion=version.get('maxVersion'),
                severity=version.get('severity'),
                vulnerabilitystatus=version.get('vulnerability'))

            if 'targetApplication' in version:
                targetApplication = etree.SubElement(
                    versionRange, 'targetApplication',
                    id=version['targetApplication']['id'])
                taVersionRange = etree.SubElement(
                    targetApplication, 'versionRange',
                    minVersion=version['targetApplication']['minVersion'],
                    maxVersion=version['targetApplication']['maxVersion'])



def write_plugin_items(xml_tree, records):
    """Generate the plugin blocklists.

    <pluginItem blockID="p422">
        <match name="filename" exp="JavaAppletPlugin\.plugin"/>
        <versionRange minVersion="Java 7 Update 16" maxVersion="Java 7 Update 24" severity="0" vulnerabilitystatus="1">
            <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
                <versionRange minVersion="17.0" maxVersion="*"/>
            </targetApplication>
        </versionRange>
    </pluginItem>
    """

    pluginItems = etree.SubElement(xml_tree, 'pluginItems')
    for item in records:
        if item['enabled']:
            entry = etree.SubElement(pluginItems, 'pluginItem',
                                     blockID=item.get('blockID'))
            if 'matchName' in item:
                match = etree.SubElement(entry, 'match',
                                         name='name',
                                         exp=item['matchName'])
            if 'matchFilename' in item:
                match = etree.SubElement(entry, 'match',
                                         name='filename',
                                         exp=item['matchFilename'])
            if 'matchDescription' in item:
                match = etree.SubElement(entry, 'match',
                                         name='description',
                                         exp=item['matchDescription'])

            if 'infoURL' in item:
                infoURL = etree.SubElement(entry, 'infoURL')
                infoURL.text = item['infoURL']

            for version in item['versionRange']:
                versionRange = etree.SubElement(
                    entry, 'versionRange',
                    minVersion=version['minVersion'] or None,
                    maxVersion=version['maxVersion'] or None,
                    severity=version['severity'] or None,
                    vulnerabilitystatus=version.get('vulnerability'))

                if 'targetApplication' in version:
                    targetApplication = etree.SubElement(
                        versionRange, 'targetApplication',
                        id=version['targetApplication']['id'])
                    taVersionRange = etree.SubElement(
                        targetApplication, 'versionRange',
                        minVersion=version['targetApplication']['minVersion'],
                        maxVersion=version['targetApplication']['maxVersion'])


def write_gfx_items(xml_tree, records):
    """Generate the gfxBlacklistEntry.

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
    """
    gfxItems = etree.SubElement(xml_tree, 'gfxItems')
    for item in records:
        if item['enabled']:
            entry = etree.SubElement(gfxItems, 'gfxBlacklistEntry',
                                     blockID=item.get('blockID'))
            # OS
            os = etree.SubElement(entry, 'os')
            os.text = item['os']

            # Vendor
            vendor = etree.SubElement(entry, 'vendor')
            vendor.text = item['vendor']

            # Devices
            devices = etree.SubElement(entry, 'devices')
            for d in item['devices']:
                device = etree.SubElement(devices, 'device')
                device.text = d

            # Feature
            feature = etree.SubElement(entry, 'feature')
            feature.text = item['feature']
            featureStatus = etree.SubElement(entry, 'featureStatus')
            featureStatus.text = item['featureStatus']

            # Driver
            driverVersion = etree.SubElement(entry, 'driverVersion')
            driverVersion.text = item['driverVersion']
            driverVersionComparator = etree.SubElement(
                entry, 'driverVersionComparator')
            driverVersionComparator.text = item['driverVersionComparator']


def write_cert_items(xml_tree, records):
    """Generate the certificate blocklists.

    <certItem issuerName="MIGQMQswCQYD...IENB">
      <serialNumber>UoRGnb96CUDTxIqVry6LBg==</serialNumber>
    </certItem>
    """
    certItems = etree.SubElement(xml_tree, 'certItems')
    for item in records:
        if item['enabled']:
            cert = etree.SubElement(certItems, 'certItem',
                                    issuerName=item['issuerName'])
            serialNumber = etree.SubElement(cert, 'serialNumber')
            serialNumber.text = item['issuerName']


def main():
    parser = cli_utils.set_parser_server_options(
        description='Build a blocklists.xml file.', default_collection=None)

    # Remove the collection arguments which is not accurate here
    # because we handle four of them in the bucket.
    remove_action(parser, '-c', '--collection')

    # Choose where to write the file down.
    parser.add_argument('-o', '--out', help='Folder to download files in.',
                        type=str, default='STDOUT')
    args = parser.parse_args()
    args.collection = None

    cli_utils.setup_logger(logger, args)

    close_out_fd = False
    if args.out.upper() == 'STDOUT':
        out_fd = sys.stdout
    elif args.out.upper() == 'STDERR':
        out_fd = sys.stderr
    else:
        out_fd = open(args.out, 'w+')
        close_out_fd = True

    client = cli_utils.create_client_from_args(args)

    last_update = 0
    # Retrieve the collection of records.
    try:
        addons_records = client.get_records(collection='addons',
                                        _sort="last_modified")
    except:
        logger.warn('Unable to fetch the ``addons`` collection.')
        addons_records = []

    if addons_records:
        last_update = addons_records[-1]['last_modified']

    try:
        plugin_records = client.get_records(collection='plugins',
                                            _sort="last_modified")
    except:
        logger.warn('Unable to fetch the ``plugins`` collection.')
        plugin_records = []

    if plugin_records:
        last_update = max(last_update, plugin_records[-1]['last_modified'])

    try:
        gfx_records = client.get_records(collection='gfx',
                                         _sort="last_modified")
    except:
        logger.warn('Unable to fetch the ``gfx`` collection.')
        gfx_records = []

    if gfx_records:
        last_update = max(last_update, gfx_records[-1]['last_modified'])

    try:
        cert_records = client.get_records(collection='certificates',
                                          _sort="last_modified")
    except:
        logger.warn('Unable to fetch the ``certificates`` collection.')
        cert_records = []

    if cert_records:
        last_update = max(last_update, cert_records[-1]['last_modified'])

    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='%s' % last_update
    )

    write_addons_items(xml_tree, addons_records)
    write_plugin_items(xml_tree, plugin_records)
    write_gfx_items(xml_tree, gfx_records)
    write_cert_items(xml_tree, cert_records)

    doc = etree.ElementTree(xml_tree)
    out_fd.write(etree.tostring(
        doc,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8'))

    if close_out_fd:
        out_fd.close()


if __name__ == '__main__':
    main()
