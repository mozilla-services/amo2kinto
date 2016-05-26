from functools import partial


def update_schema_if_mandatory(response, config, patch_collection):
    if 'details' in response:
        collection_schema = {
            'schema': response['details']['existing'].get('schema'),
            'uiSchema': response['details']['existing'].get('uiSchema'),
            'displayFields': response['details']['existing'].get(
                'displayFields'),
        }
    else:
        collection_schema = {
            'schema': response['data'].get('schema'),
            'uiSchema': response['data'].get('uiSchema'),
            'displayFields': response['data'].get('displayFields'),
        }

    if config and collection_schema != config:
        patch_collection(data=config)


def get_kinto_records(kinto_client, bucket, collection, permissions,
                      config=None):
    """Return all the kinto records for this bucket/collection."""
    # Create bucket if needed
    kinto_client.create_bucket(bucket, if_not_exists=True)
    response = kinto_client.create_collection(
        collection, bucket, permissions=permissions, if_not_exists=True)

    patch_collection = partial(kinto_client.patch_collection,
                               bucket=bucket, collection=collection)

    update_schema_if_mandatory(response, config, patch_collection)

    return kinto_client.get_records(bucket=bucket, collection=collection)
