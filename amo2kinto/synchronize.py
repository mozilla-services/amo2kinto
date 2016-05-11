from .logger import logger


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

    return ([source_dict[k] for k in to_create],
            [dest_dict[k] for k in to_delete])


def push_changes(diff, kinto_client, bucket, collection):
    to_create, to_delete = diff

    logger.warn('Syncing to {}{}'.format(
        kinto_client.session_kwargs['server_url'],
        kinto_client.endpoints.get(
            'records', bucket=bucket, collection=collection)))

    logger.info('- {} records to create.'.format(len(to_create)))
    logger.info('- {} records to delete.'.format(len(to_delete)))

    with kinto_client.batch(bucket=bucket, collection=collection) as batch:
        for record in to_delete:
            batch.delete_record(record)
        for record in to_create:
            # Records are enabled by default.
            record['enabled'] = True
            batch.create_record(record)

    if to_create or to_delete:
        logger.info('Trigger the signature.')

        # Trigger signature once modifications where done.
        kinto_client.patch_collection(data={'status': 'to-sign'},
                                      bucket=bucket, collection=collection)

    logger.info('Done!')
