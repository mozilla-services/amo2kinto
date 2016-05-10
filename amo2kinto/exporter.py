import sys
from collections import OrderedDict
from lxml import etree
from kinto_client import cli_utils
from . import constants
from .compare import version_int

from .logger import logger


def build_version_range(root, item, app_id, app_ver=None):
    for version in item['versionRange']:
        is_version_related_to_app = (
            not version.get('targetApplication') or
            any(tA for tA in version.get('targetApplication', [])
                if not tA.get('guid') or tA.get('guid') == app_id))

        if is_version_related_to_app:
            versionRange = etree.SubElement(
                root, 'versionRange')

            for field in ['minVersion', 'maxVersion', 'severity']:
                value = version.get(field)
                if value:
                    versionRange.set(field, str(value))

            has_targetApplication = (
                'targetApplication' in version and version['targetApplication']
            )

            if has_targetApplication:
                for tA in version['targetApplication']:
                    is_targetApp_related = (
                        not tA['guid'] or tA['guid'] == app_id
                    )
                    if is_targetApp_related:
                        targetApplication = etree.SubElement(
                            versionRange, 'targetApplication',
                            id=tA['guid'])
                        etree.SubElement(
                            targetApplication, 'versionRange',
                            minVersion=tA['minVersion'],
                            maxVersion=tA['maxVersion'])


def is_related_to(item, app_id):
    """Return True if the item relates to the given app_id."""
    if not item.get('versionRange'):
        return True

    for vR in item['versionRange']:
        if not vR.get('targetApplication'):
            return True

        for tA in vR['targetApplication']:
            if tA['guid'] == app_id:
                return True

    return False


def write_addons_items(xml_tree, records, app_id, api_ver=3):
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
        if is_related_to(item, app_id):
            emItem = etree.SubElement(emItems, 'emItem',
                                      blockID=item.get('blockID', item['id']))

            for field in ['name', 'os']:
                if field in item:
                    emItem.set(field, item[field])

            if 'guid' in item:
                emItem.set('id', item['guid'])

            prefs = etree.SubElement(emItem, 'prefs')
            for p in item['prefs']:
                pref = etree.SubElement(prefs, 'pref')
                pref.text = p

            build_version_range(emItem, item, app_id)


def between(ver, min, max):
    if not (min and max):
        return True
    return version_int(min) < ver < version_int(max)


def write_plugin_items(xml_tree, records, app_id, api_ver=3, app_ver=None):
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
        if is_related_to(item, app_id):
            for versionRange in item.get('versionRange', []):
                if not versionRange.get('targetApplication'):
                    add_plugin_item(pluginItems, item, versionRange,
                                    app_id=app_id, api_ver=api_ver,
                                    app_ver=app_ver)
                else:
                    for targetApplication in versionRange['targetApplication']:
                        is_targetApplication_related = (
                            'guid' not in targetApplication or
                            targetApplication['guid'] == app_id
                        )
                        if is_targetApplication_related:
                            if api_ver < 3 and app_ver is not None:
                                app_version = version_int(app_ver)
                                is_version_related = between(
                                    app_version,
                                    targetApplication.get('minVersion', 0),
                                    targetApplication.get('maxVersion', '*'))
                                if is_version_related:
                                    add_plugin_item(
                                        pluginItems, item, versionRange,
                                        targetApplication, app_id=app_id,
                                        api_ver=api_ver, app_ver=app_ver)
                            else:
                                add_plugin_item(
                                    pluginItems, item, versionRange,
                                    targetApplication, app_id=app_id,
                                    api_ver=api_ver, app_ver=app_ver)


def add_plugin_item(pluginItems, item, version, tA=None, app_id=None,
                    api_ver=3, app_ver=None):

    entry = etree.SubElement(pluginItems, 'pluginItem',
                             blockID=item.get('blockID', item['id']))

    for field in ['name', 'os', 'xpcomabi']:
        if field in item:
            entry.set(field, item[field])

    for xml_field in ['name', 'filename', 'description']:
        json_field = 'match%s' % xml_field.capitalize()
        if json_field in item:
            etree.SubElement(entry, 'match',
                             name=xml_field,
                             exp=item[json_field])

    if 'infoURL' in item:
        infoURL = etree.SubElement(entry, 'infoURL')
        infoURL.text = item['infoURL']

    minVersion = version.get('minVersion')
    maxVersion = version.get('maxVersion')
    severity = version.get('severity')
    vulnerabilityStatus = version.get('vulnerabilityStatus')

    app_guid = tA and tA.get('guid') or None

    kwargs = OrderedDict()
    force_empty_versionRange = False

    # Condition taken exactly as they were in addons-server code.
    if (severity or app_guid or (minVersion and maxVersion) or
            vulnerabilityStatus):
        if app_guid:
            if minVersion and maxVersion:
                kwargs['maxVersion'] = maxVersion
                kwargs['minVersion'] = minVersion
                if severity is not None:
                    kwargs['severity'] = str(severity)
                if vulnerabilityStatus:
                    kwargs['vulnerabilitystatus'] = str(vulnerabilityStatus)
            else:
                force_empty_versionRange = True
                if severity is not None:
                    kwargs['severity'] = str(severity)
                if vulnerabilityStatus is not None:
                    kwargs['vulnerabilitystatus'] = str(vulnerabilityStatus)

        elif api_ver > 2 and minVersion and maxVersion:
            kwargs['maxVersion'] = maxVersion
            kwargs['minVersion'] = minVersion
            if severity is not None:
                kwargs['severity'] = str(severity)
            if vulnerabilityStatus is not None:
                kwargs['vulnerabilitystatus'] = str(vulnerabilityStatus)

        elif severity and not (minVersion or maxVersion):
            kwargs['severity'] = str(severity)

        elif vulnerabilityStatus:
            if severity is not None:
                kwargs['severity'] = str(severity)
            kwargs['vulnerabilitystatus'] = str(vulnerabilityStatus)

    elif severity == 0:
        kwargs['severity'] = str(severity)

    versionRange_not_null = (
        len(kwargs.keys()) or (api_ver > 2 and tA and tA.get(
            'minVersion') and tA.get('maxVersion'))
    )

    if versionRange_not_null or force_empty_versionRange:
        versionRange = etree.SubElement(entry, 'versionRange', **kwargs)

    is_targetApplication_applicable = (api_ver > 2 and
                                       tA and
                                       tA.get('minVersion') and
                                       tA.get('maxVersion'))

    if is_targetApplication_applicable:
        targetApplication = etree.SubElement(
            versionRange, 'targetApplication',
            id=tA['guid'])
        etree.SubElement(targetApplication,
                         'versionRange',
                         minVersion=tA['minVersion'],
                         maxVersion=tA['maxVersion'])


def write_gfx_items(xml_tree, records, app_id, api_ver=3):
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
        is_record_related = ('guid' not in item or item['guid'] == app_id)

        if is_record_related:
            entry = etree.SubElement(gfxItems, 'gfxBlacklistEntry',
                                     blockID=item.get('blockID', item['id']))
            fields = ['os', 'vendor', 'feature', 'featureStatus',
                      'driverVersion', 'driverVersionComparator']
            for field in fields:
                if field in item:
                    node = etree.SubElement(entry, field)
                    node.text = item[field]

            # Devices
            if item['devices']:
                devices = etree.SubElement(entry, 'devices')
                for d in item['devices']:
                    device = etree.SubElement(devices, 'device')
                    device.text = d


def write_cert_items(xml_tree, records, api_ver=3):
    """Generate the certificate blocklists.

    <certItem issuerName="MIGQMQswCQYD...IENB">
      <serialNumber>UoRGnb96CUDTxIqVry6LBg==</serialNumber>
    </certItem>
    """
    if not records:
        return

    certItems = etree.SubElement(xml_tree, 'certItems')
    for item in records:
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
            enabled=True,
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
            enabled=True,
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
            enabled=True,
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
            enabled=True,
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
