import json

from six import iteritems

from .logger import logger


def strip_keys(record, keys=['id', 'last_modified', 'enabled']):
    return {key: value for key, value in iteritems(record) if key not in keys}


def canonical_json(record):
    return json.dumps(strip_keys(record),
                      sort_keys=True,
                      separators=(',', ':'))


def get_diff(source, dest):
    """Get the diff between two records list in this order:
        - to_create
        - to_delete
    """
    # First build a dict from the lists, with the ID as the key.
    source_dict = {record['id']: record for record in source}
    dest_dict = {record['id']: record for record in dest}

    source_keys = set(source_dict.keys())
    dest_keys = set(dest_dict.keys())
    to_create = source_keys - dest_keys
    to_delete = dest_keys - source_keys
    to_update = set()

    to_check = source_keys - to_create - to_delete

    for record_id in to_check:
        # Make sure to remove properties that are part of kinto
        # records and not amo records.
        # Here we will compare the record properties ignoring:
        # ID, last_modified and enabled.
        new = canonical_json(source_dict[record_id])
        old = canonical_json(dest_dict[record_id])
        if new != old:
            to_update.add(record_id)

    return ([source_dict[k] for k in to_create],
            [source_dict[k] for k in to_update],
            [dest_dict[k] for k in to_delete])


def push_changes(diff, kinto_client, bucket, collection):
    to_create, to_update, to_delete = diff

    logger.warn('Syncing to {}{}'.format(
        kinto_client.session_kwargs['server_url'],
        kinto_client.endpoints.get(
            'records', bucket=bucket, collection=collection)))

    logger.info('- {} records to create.'.format(len(to_create)))
    logger.info('- {} records to delete.'.format(len(to_delete)))

    with kinto_client.batch(bucket=bucket, collection=collection) as batch:
        for record in to_delete:
            batch.delete_record(record['id'])
        for record in to_create:
            # Records are enabled by default.
            record['enabled'] = True
            batch.create_record(record)
        for record in to_update:
            # Patch the record with the new properties from AMO.
            # This will override changes that were made before in
            # Kinto if any. But json2kinto should be used only to
            # rsync AMO database so it is fine.
            patch_record = strip_keys(record, ['id'])
            # Make sure the record is correcly activated.
            patch_record['enabled'] = True
            batch.patch_record(patch_record)

    if to_create or to_update or to_delete:
        logger.info('Trigger the signature.')

        # Trigger signature once modifications where done.
        kinto_client.patch_collection(data={'status': 'to-sign'},
                                      bucket=bucket, collection=collection)

    logger.info('Done!')
