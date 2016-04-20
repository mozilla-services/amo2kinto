import logging
import sys
from lxml import etree
from kinto_client import cli_utils
from . import constants

logger = logging.getLogger("kinto2xml")


def build_version_range(root, item, app_id, app_ver=None,
                        ignore_empty_severity=False):
    for version in item['versionRange']:
        versionRange = etree.SubElement(
            root, 'versionRange')
        minVersion = version.get('minVersion')

        if minVersion:
            versionRange.set('minVersion', minVersion)

        maxVersion = version.get('maxVersion')
        if maxVersion:
            versionRange.set('maxVersion', maxVersion)

        severity = version.get('severity')

        add_severity = bool(severity)

        if not ignore_empty_severity:
            add_severity = severity or severity == 0

        if add_severity:
            versionRange.set('severity', str(severity))

        vulnerabilityStatus = version.get('vulnerabilityStatus')
        if vulnerabilityStatus:
            versionRange.set('vulnerabilitystatus', str(vulnerabilityStatus))

        if ('targetApplication' in version and
                version['targetApplication']):
            for tA in version['targetApplication']:
                if not tA['guid'] or tA['guid'] == app_id:
                    targetApplication = etree.SubElement(
                        versionRange, 'targetApplication',
                        id=tA['guid'])
                    etree.SubElement(
                        targetApplication, 'versionRange',
                        minVersion=tA['minVersion'],
                        maxVersion=tA['maxVersion'])


def is_related_to(item, app_id):
    """Return True if the item relate ot the given app_id."""
    if not item.get('versionRange'):
        return True

    for vR in item['versionRange']:
        if not vR.get('targetApplication'):
            return True

        for tA in vR['targetApplication']:
            if tA['guid'] == app_id:
                return True
    return False


def write_addons_items(xml_tree, records, app_id):
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
    if not records:
        return

    emItems = etree.SubElement(xml_tree, 'emItems')
    for item in records:
        if item.get('enabled', True) and is_related_to(item, app_id):
            emItem = etree.SubElement(emItems, 'emItem',
                                      blockID=item.get('blockID', item['id']))

            if 'name' in item:
                emItem.set('name', item['name'])

            if 'os' in item:
                emItem.set('os', item['os'])

            if 'guid' in item:
                emItem.set('id', item['guid'])

            prefs = etree.SubElement(emItem, 'prefs')
            for p in item['prefs']:
                pref = etree.SubElement(prefs, 'pref')
                pref.text = p

            build_version_range(emItem, item, app_id,
                                ignore_empty_severity=True)


def write_plugin_items(xml_tree, records, app_id):
    """Generate the plugin blocklists.

    <pluginItem blockID="p422">
        <match name="filename" exp="JavaAppletPlugin\.plugin"/>
        <versionRange minVersion="Java 7 Update 16"
                      maxVersion="Java 7 Update 24"
                      severity="0" vulnerabilitystatus="1">
            <targetApplication id="{ec8030f7-c20a-464f-9b0e-13a3a9e97384}">
                <versionRange minVersion="17.0" maxVersion="*"/>
            </targetApplication>
        </versionRange>
    </pluginItem>
    """

    if not records:
        return

    pluginItems = etree.SubElement(xml_tree, 'pluginItems')
    for item in records:
        if item.get('enabled', True) and is_related_to(item, app_id):
            for versionRange in item.get('versionRange', []):
                if not versionRange.get('targetApplication'):
                    add_plugin_item(pluginItems, item, versionRange)
                else:
                    for targetApplication in versionRange['targetApplication']:
                        if 'guid' not in targetApplication or \
                           targetApplication['guid'] == app_id:
                            add_plugin_item(pluginItems, item, versionRange,
                                            targetApplication)


def add_plugin_item(pluginItems, item, version, tA=None,
                    ignore_empty_severity=False):
    entry = etree.SubElement(pluginItems, 'pluginItem',
                             blockID=item.get('blockID', item['id']))

    if 'name' in item:
        entry.set('name', item['name'])

    if 'os' in item:
        entry.set('os', item['os'])

    if 'xpcomabi' in item:
        entry.set('xpcomabi', item['xpcomabi'])

    if 'matchName' in item:
        etree.SubElement(entry, 'match',
                         name='name',
                         exp=item['matchName'])
    if 'matchFilename' in item:
        etree.SubElement(entry, 'match',
                         name='filename',
                         exp=item['matchFilename'])
    if 'matchDescription' in item:
        etree.SubElement(entry, 'match',
                         name='description',
                         exp=item['matchDescription'])

    if 'infoURL' in item:
        infoURL = etree.SubElement(entry, 'infoURL')
        infoURL.text = item['infoURL']

    minVersion = version.get('minVersion')
    maxVersion = version.get('maxVersion')
    severity = version.get('severity')
    add_severity = bool(severity)
    if not ignore_empty_severity:
        add_severity = severity or severity == 0

    vulnerabilityStatus = version.get('vulnerabilityStatus')
    add_tA = tA and tA.get('minVersion') and tA.get('maxVersion')

    if (minVersion and maxVersion) or add_severity or \
       vulnerabilityStatus or add_tA:
        versionRange = etree.SubElement(entry, 'versionRange')

        if minVersion and maxVersion:
            versionRange.set('minVersion', minVersion)
            versionRange.set('maxVersion', maxVersion)

        if add_severity:
            versionRange.set('severity', str(severity))

        if vulnerabilityStatus:
            versionRange.set('vulnerabilitystatus', str(vulnerabilityStatus))

        if tA and tA.get('minVersion') and tA.get('maxVersion'):
            targetApplication = etree.SubElement(
                versionRange, 'targetApplication',
                id=tA['guid'])
            etree.SubElement(
                targetApplication, 'versionRange',
                minVersion=tA['minVersion'],
                maxVersion=tA['maxVersion'])


def write_gfx_items(xml_tree, records, app_id):
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
    if not records:
        return

    gfxItems = etree.SubElement(xml_tree, 'gfxItems')
    for item in records:
        if ('guid' not in item or item['guid'] == app_id) and \
           item.get('enabled', True):
            entry = etree.SubElement(gfxItems, 'gfxBlacklistEntry',
                                     blockID=item.get('blockID', item['id']))
            # OS
            os = etree.SubElement(entry, 'os')
            os.text = item['os']

            # Vendor
            vendor = etree.SubElement(entry, 'vendor')
            vendor.text = item['vendor']

            # Devices
            if item['devices']:
                devices = etree.SubElement(entry, 'devices')
                for d in item['devices']:
                    device = etree.SubElement(devices, 'device')
                    device.text = d

            # Feature
            if 'feature' in item:
                feature = etree.SubElement(entry, 'feature')
                feature.text = item['feature']

            if 'featureStatus' in item:
                featureStatus = etree.SubElement(entry, 'featureStatus')
                featureStatus.text = item['featureStatus']

            # Driver
            if 'driverVersion' in item:
                driverVersion = etree.SubElement(entry, 'driverVersion')
                driverVersion.text = item['driverVersion']
            if 'driverVersionComparator' in item:
                driverVersionComparator = etree.SubElement(
                    entry, 'driverVersionComparator')
                driverVersionComparator.text = item['driverVersionComparator']


def write_cert_items(xml_tree, records):
    """Generate the certificate blocklists.

    <certItem issuerName="MIGQMQswCQYD...IENB">
      <serialNumber>UoRGnb96CUDTxIqVry6LBg==</serialNumber>
    </certItem>
    """
    if not records:
        return

    certItems = etree.SubElement(xml_tree, 'certItems')
    for item in records:
        if item.get('enabled', True):
            cert = etree.SubElement(certItems, 'certItem',
                                    issuerName=item['issuerName'])
            serialNumber = etree.SubElement(cert, 'serialNumber')
            serialNumber.text = item['serialNumber']


def main(args=None):
    parser = cli_utils.add_parser_options(
        description='Build a blocklists.xml file from Kinto blocklists.',
        default_collection=None,
        default_bucket=None,
        default_server=constants.KINTO_SERVER,
        default_auth=constants.AUTH,
        include_bucket=False,
        include_collection=False)

    parser.add_argument('--certificates-bucket',
                        help='Bucket name for certificates',
                        type=str, default=constants.CERT_BUCKET)

    parser.add_argument('--certificates-collection',
                        help='Collection name for certificates',
                        type=str, default=constants.CERT_COLLECTION)

    parser.add_argument('--gfx-bucket', help='Bucket name for gfx',
                        type=str, default=constants.GFX_BUCKET)

    parser.add_argument('--gfx-collection',
                        help='Collection name for gfx',
                        type=str, default=constants.GFX_COLLECTION)

    parser.add_argument('--addons-bucket', help='Bucket name for addons',
                        type=str, default=constants.ADDONS_BUCKET)

    parser.add_argument('--addons-collection',
                        help='Collection name for addon',
                        type=str, default=constants.ADDONS_COLLECTION)

    parser.add_argument('--plugins-bucket', help='Bucket name for plugins',
                        type=str, default=constants.PLUGINS_BUCKET)

    parser.add_argument('--plugins-collection',
                        help='Collection name for plugin',
                        type=str, default=constants.PLUGINS_COLLECTION)

    parser.add_argument('--app', help='Targeted blocklists.xml APP id',
                        type=str, default=constants.FIREFOX_APPID)

    # Choose where to write the file down.
    parser.add_argument('-o', '--out', help='Output XML file.',
                        type=str, default=None)

    args = parser.parse_args(args=args)

    cli_utils.setup_logger(logger, args)

    if not args.out:
        out_fd = sys.stdout
        close_out_fd = False
    else:
        out_fd = open(args.out, 'w+')
        close_out_fd = True

    client = cli_utils.create_client_from_args(args)

    last_update = 0
    # Retrieve the collection of records.
    try:
        addons_records = client.get_records(
            bucket=args.addons_bucket,
            collection=args.addons_collection,
            _sort="last_modified")
    except:
        logger.warn(
            'Unable to fetch the ``{bucket}/{collection}`` records.'.format(
                bucket=args.addons_bucket,
                collection=args.addons_collection,
            )
        )
        addons_records = []

    if addons_records:
        last_update = addons_records[-1]['last_modified']

    try:
        plugin_records = client.get_records(
            bucket=args.plugins_bucket,
            collection=args.plugins_collection,
            _sort="last_modified")
    except:
        logger.warn(
            'Unable to fetch the ``{bucket}/{collection}`` records.'.format(
                bucket=args.plugins_bucket,
                collection=args.plugins_collection,
            )
        )
        plugin_records = []

    if plugin_records:
        last_update = max(last_update, plugin_records[-1]['last_modified'])

    try:
        gfx_records = client.get_records(
            bucket=args.gfx_bucket,
            collection=args.gfx_collection,
            _sort="last_modified")
    except:
        logger.warn(
            'Unable to fetch the ``{bucket}/{collection}`` records.'.format(
                bucket=args.gfx_bucket,
                collection=args.gfx_collection,
            )
        )
        gfx_records = []

    if gfx_records:
        last_update = max(last_update, gfx_records[-1]['last_modified'])

    try:
        cert_records = client.get_records(
            bucket=args.certificates_bucket,
            collection=args.certificates_collection,
            _sort="last_modified")
    except:
        logger.warn(
            'Unable to fetch the ``{bucket}/{collection}`` records.'.format(
                bucket=args.certificates_bucket,
                collection=args.certificates_collection,
            )
        )
        cert_records = []

    if cert_records:
        last_update = max(last_update, cert_records[-1]['last_modified'])

    xml_tree = etree.Element(
        'blocklist',
        xmlns="http://www.mozilla.org/2006/addons-blocklist",
        lastupdate='%s' % last_update
    )

    write_addons_items(xml_tree, addons_records, app_id=args.app)
    write_plugin_items(xml_tree, plugin_records, app_id=args.app)
    write_gfx_items(xml_tree, gfx_records, app_id=args.app)
    write_cert_items(xml_tree, cert_records)

    doc = etree.ElementTree(xml_tree)
    out_fd.write(etree.tostring(
        doc,
        pretty_print=True,
        xml_declaration=True,
        encoding='UTF-8').decode('utf-8'))

    if close_out_fd:
        out_fd.close()
