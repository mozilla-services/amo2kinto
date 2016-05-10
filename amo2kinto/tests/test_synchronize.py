import mock
import unittest

from contextlib import contextmanager
from amo2kinto.synchronize import get_diff, push_changes


def test_get_diff():
    source = [{'id': 1, 'val': 2}, {'id': 2, 'val': 3}]
    dest = [{'id': 2, 'val': 3}, {'id': 3, 'val': 4}]
    assert get_diff(source, dest) == (
        [{'id': 1, 'val': 2}],
        [{'id': 3, 'val': 4}])


class SynchronizeTest(unittest.TestCase):

    def setUp(self):
        self.mocked_batch = mock.MagicMock()

        @contextmanager
        def mocked_context_manager(bucket, collection):
            yield self.mocked_batch

        self.kinto_client = mock.MagicMock()
        self.kinto_client.batch = mocked_context_manager
        self.bucket = mock.sentinel.bucket
        self.collection = mock.sentinel.collection

    def test_synchronize_create_the_batch_request(self):
        push_changes(([{'id': 1, 'val': 2}], [{'id': 3, 'val': 4}]),
                     self.kinto_client, self.bucket, self.collection)

        self.mocked_batch.create_record.assert_called_with(
            {'id': 1, 'val': 2, 'enabled': True})
        self.mocked_batch.delete_record.assert_called_with(
            {'id': 3, 'val': 4})

    def test_synchronize_triggers_the_signature(self):
        push_changes(([{'id': 1, 'val': 2}], [{'id': 3, 'val': 4}]),
                     self.kinto_client, self.bucket, self.collection)

        self.kinto_client.patch_collection.assert_called_with(
            data={'status': 'to-sign'},
            bucket=mock.sentinel.bucket, collection=mock.sentinel.collection)

    def test_synchronize_does_not_triggers_the_signer_on_empty_changes(self):
        push_changes(([], []), self.kinto_client, self.bucket, self.collection)

        self.assertFalse(self.kinto_client.patch_collection.called)
