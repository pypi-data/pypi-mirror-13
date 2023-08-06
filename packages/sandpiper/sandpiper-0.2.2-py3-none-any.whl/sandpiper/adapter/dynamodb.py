import decimal
import json

from .abstract import Abstract

class DynamoDB(object):
    def __init__(self, storage, namespace = 'default'):
        self._namespace = namespace
        self._storage   = storage

    def get(self, key):
        response = self._table().get_item(Key = {'key': key})

        item = response['Item'] if 'Item' in response else None

        return item['value'] if item else None

    def set(self, key, value):
        self._table().put_item(Item = self._prepare_for_setter({
            'key':   key,
            'value': value,
        }))

    def remove(self, key):
        self._table().delete_item(Key = {'key': key})

    def _table_name(self):
        return self._namespace

    def _table(self):
        return self._storage.Table(self._table_name())

    def _prepare_for_setter(self, data):
        return self._decode(json.dumps(data))

    def _decode(self, data):
        return json.loads(data, parse_float = decimal.Decimal)

    def prepare(self, **kwargs):
        throughput = {
            'ReadCapacityUnits':  kwargs['io_read']  if 'io_read'  in kwargs else 5,
            'WriteCapacityUnits': kwargs['io_write'] if 'io_write' in kwargs else 4,
        }

        self._storage.create_table(
            TableName = self._table_name(),
            KeySchema = [
                {
                    'AttributeName': 'key',
                    'KeyType': 'HASH'
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': 'key',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput = throughput
        )
