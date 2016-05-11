from functools import partial


def update_schema_if_mandatory(response, schema, patch_collection):
    if 'details' in response:
        collection_schema = response['details']['existing']['schema']
    else:
        collection_schema = response['data'].get('schema')

    if schema and (not collection_schema or collection_schema != schema):
        patch_collection(data={'schema': schema})


def get_kinto_records(kinto_client, bucket, collection, permissions,
                      schema=None):
    """Return all the kinto records for this bucket/collection."""
    # Create bucket if needed
    kinto_client.create_bucket(bucket, if_not_exists=True)
    response = kinto_client.create_collection(
        collection, bucket, permissions=permissions, if_not_exists=True)

    patch_collection = partial(kinto_client.patch_collection,
                               bucket=bucket, collection=collection)

    update_schema_if_mandatory(response, schema, patch_collection)

    return kinto_client.get_records(bucket=bucket, collection=collection)
