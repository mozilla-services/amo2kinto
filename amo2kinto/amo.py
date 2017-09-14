import hashlib
import uuid


def make_id_from_string(string):
    hashed = hashlib.md5(string.encode('utf-8'))
    return str(uuid.UUID(hashed.hexdigest()))


def prepare_amo_records(records, fields):
    for record in records:
        blockID = record['blockID']

        # Remove fields we do not want to keep.
        for field in list(record.keys()):
            if field not in fields:
                del record[field]
            else:
                if isinstance(record[field], str):
                    record[field] = record[field].strip()

        record['id'] = make_id_from_string(blockID)

    return records  # for convenience
