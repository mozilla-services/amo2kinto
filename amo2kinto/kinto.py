from kinto_http.exceptions import KintoException


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
        kinto_client.create_collection(id=collection, bucket=bucket,
                                       permissions=permissions, if_not_exists=True)
    except KintoException as e:
        if hasattr(e, 'response') and e.response.status_code == 403:
            # The user cannot create collection on this bucket, ignore the creation.
            pass

    return kinto_client.get_records(bucket=bucket, collection=collection)
