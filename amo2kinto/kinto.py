from functools import partial
from kinto_http.exceptions import KintoException


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
    try:
        kinto_client.create_bucket(id=bucket, if_not_exists=True)
    except KintoException as e:
        if hasattr(e, 'response') and e.response.status_code == 403:
            # The user cannot create buckets on this server, ignore the creation.
            pass

    try:
        response = kinto_client.create_collection(
            id=collection, bucket=bucket, permissions=permissions, if_not_exists=True)
    except KintoException as e:
        if hasattr(e, 'response') and e.response.status_code == 403:
            # The user cannot create collection on this bucket, ignore the creation.
            pass
        response = kinto_client.get_collection(id=collection, bucket=bucket)

    patch_collection = partial(kinto_client.patch_collection,
                               bucket=bucket, id=collection)

    update_schema_if_mandatory(response, config, patch_collection)

    return kinto_client.get_records(bucket=bucket, collection=collection)
