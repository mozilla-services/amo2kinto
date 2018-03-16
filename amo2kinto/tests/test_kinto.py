import mock
from kinto_http.exceptions import KintoException
from amo2kinto.kinto import get_kinto_records


def test_get_kinto_records_try_to_create_the_bucket():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_bucket.assert_called_with(id=mock.sentinel.bucket,
                                                  if_not_exists=True)


def test_get_kinto_records_try_to_create_the_bucket_and_keep_going_on_403():
    kinto_client = mock.MagicMock()
    Http403 = mock.MagicMock()
    Http403.response.status_code = 403
    kinto_client.create_bucket.side_effect = KintoException(exception=Http403)
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_bucket.assert_called_with(id=mock.sentinel.bucket,
                                                  if_not_exists=True)
    kinto_client.create_collection.assert_called_with(
        id=mock.sentinel.collection, bucket=mock.sentinel.bucket,
        permissions=mock.sentinel.permissions, if_not_exists=True)


def test_get_kinto_records_try_to_create_the_collection_with_permissions():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_collection.assert_called_with(
        id=mock.sentinel.collection, bucket=mock.sentinel.bucket,
        permissions=mock.sentinel.permissions, if_not_exists=True)


def test_get_kinto_records_try_to_create_the_collection_and_keep_going_on_403():
    kinto_client = mock.MagicMock()
    Http403 = mock.MagicMock()
    Http403.response.status_code = 403
    kinto_client.create_collection.side_effect = KintoException(exception=Http403)
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.get_records.assert_called_with(bucket=mock.sentinel.bucket,
                                                collection=mock.sentinel.collection)


def test_get_kinto_records_gets_a_list_of_records():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.get_records.assert_called_with(
        bucket=mock.sentinel.bucket, collection=mock.sentinel.collection)
