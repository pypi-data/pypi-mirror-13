import decimal
import json

from boto3.dynamodb.conditions import Key

from .abstract import Abstract


class DynamoDB(object):
    __primary_key     = 'identifier';
    __value_attribute = 'value';

    def __init__(self, storage, namespace = 'default'):
        self._namespace = namespace
        self._storage   = storage

    def get(self, key):
        response = self._table().get_item(Key = {self.__primary_key: key})

        item = response['Item'] if 'Item' in response else None

        return item[self.__value_attribute] if item else None

    def set(self, key, value):
        self._table().put_item(Item = self._prepare_for_setter({
            self.__primary_key:     key,
            self.__value_attribute: value,
        }))

    def remove(self, key):
        self._table().delete_item(Key = {self.__primary_key: key})

    def find(self, begins_with=None, eq=None):
        key_condition = None

        if eq:
            key_condition = Key(self.__primary_key).eq(eq)
        elif begins_with:
            key_condition = Key(self.__primary_key).begins_with(begins_with)

        if not key_condition:
            raise ValueError('Need to define the search pattern.')

        response = self._table().query(KeyConditionExpression = key_condition)

        if 'Items' not in response:
            return {}

        return {
            item[self.__primary_key]: item[self.__value_attribute]
            for item in response['Items']
        }

    def prepare(self, io_read = 5, io_write = 4):
        throughput = {
            'ReadCapacityUnits':  io_read,
            'WriteCapacityUnits': io_write,
        }

        self._storage.create_table(
            TableName = self._table_name(),
            KeySchema = [
                {
                    'AttributeName': self.__primary_key,
                    'KeyType':       'HASH',
                }
            ],
            AttributeDefinitions = [
                {
                    'AttributeName': self.__primary_key,
                    'AttributeType': 'S',
                }
            ],
            ProvisionedThroughput = throughput
        )

    def _table_name(self):
        return self._namespace

    def _table(self):
        return self._storage.Table(self._table_name())

    def _prepare_for_setter(self, data):
        return self._decode(json.dumps(data))

    def _decode(self, data):
        return json.loads(data, parse_float = decimal.Decimal)
