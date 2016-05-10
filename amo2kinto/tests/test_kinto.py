import mock
from amo2kinto.kinto import get_kinto_records


def test_get_kinto_records_try_to_create_the_bucket():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_bucket.assert_called_with(mock.sentinel.bucket,
                                                  if_not_exists=True)


def test_get_kinto_records_try_to_create_the_collection_with_permissions():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.create_collection.assert_called_with(
        mock.sentinel.collection, mock.sentinel.bucket,
        permissions=mock.sentinel.permissions, if_not_exists=True)


def test_get_kinto_records_gets_a_list_of_records():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    get_kinto_records(kinto_client, mock.sentinel.bucket,
                      mock.sentinel.collection, mock.sentinel.permissions)

    kinto_client.get_records.assert_called_with(
        bucket=mock.sentinel.bucket, collection=mock.sentinel.collection)


def test_get_kinto_records_try_to_create_the_collection_with_schema():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value.status_code = 201
    kinto_client.create_collection.return_value.json.return_value = {
        "data": {
            "schema": {}
        }
    }
    get_kinto_records(kinto_client,
                      mock.sentinel.bucket,
                      mock.sentinel.collection,
                      mock.sentinel.permissions,
                      schema={'foo': 'bar'})

    kinto_client.patch_collection.assert_called_with(
        bucket=mock.sentinel.bucket,
        collection=mock.sentinel.collection,
        data={"schema": {"foo": "bar"}})


def test_get_kinto_records_try_to_update_the_collection_schema():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value = {
        "details": {
            "existing": {
                "schema": {}
            }
        }
    }
    get_kinto_records(kinto_client,
                      mock.sentinel.bucket,
                      mock.sentinel.collection,
                      mock.sentinel.permissions,
                      schema={'foo': 'bar'})

    kinto_client.patch_collection.assert_called_with(
        bucket=mock.sentinel.bucket,
        collection=mock.sentinel.collection,
        data={"schema": {"foo": "bar"}})


def test_get_kinto_records_does_not_update_the_collection_schema_if_right():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value = {
        "details": {
            "existing": {
                "schema": {"foo": "bar"}
            }
        }
    }
    get_kinto_records(kinto_client,
                      mock.sentinel.bucket,
                      mock.sentinel.collection,
                      mock.sentinel.permissions,
                      schema={'foo': 'bar'})

    assert not kinto_client.patch_collection.called


def test_get_kinto_records_does_update_if_it_has_created_it():
    kinto_client = mock.MagicMock()
    kinto_client.create_collection.return_value = {
        "data": {
            "schema": {}
        }
    }
    get_kinto_records(kinto_client,
                      mock.sentinel.bucket,
                      mock.sentinel.collection,
                      mock.sentinel.permissions,
                      schema={'foo': 'bar'})

    assert kinto_client.patch_collection.called
