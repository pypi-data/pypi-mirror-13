from __future__ import absolute_import

import json
import requests
from lambdanow.channel import ChannelCollection
from lambdanow.schema import SchemaCollection, Schema


class DataClient(object):
    _SCHEMA_URI = 'schemas'
    _CHANNELS_URI = 'channels'

    def __init__(self, data_api_url, data_api_token):
        """
        Initialize client. The URL and token can be retrieved from your
        cluster's dashboard
        :param data_api_url: The URL of data-api node.
        :param data_api_token: Authentication token to access APIs
        """
        self._api_url = data_api_url.rstrip('/')
        self._api_token = data_api_token

    def create_channel(self, name, schema, num_partitions):
        """
        Creates a channel with the given name
        and associates the channel with given schema
        :param name: Channel name
        :param schema: The fully qualified name of the schema (namespace.name)
        :param partitions_count: The number of partitions of the Kafka topic
        """
        response = requests.post(
            self._get_url(self._CHANNELS_URI),
            json={
                'name': name,
                'schema': schema,
                'partitions': num_partitions
            },
            headers=self._get_headers()
        )
        if response.status_code != requests.codes.ok:
            raise RuntimeError("Failed to create schema")

        return True

    def get_channels(self):
        """
        Gets the list of registered channels
        along with their detailed info from Kafka
        """
        response = requests.get(self._get_url(self._CHANNELS_URI),
                                headers=self._get_headers())

        return ChannelCollection(response.json())

    def register_schema(self, schema):
        """
        Use the API to register a new schema.
        :param schema: An instance of Schame to register on the backend.
        """
        if isinstance(schema, Schema):
            schema = schema.to_dict()
        else:
            schema = json.loads(schema)

        response = requests.post(self._get_url(self._SCHEMA_URI),
                                 json=schema, headers=self._get_headers())

        if response.status_code != requests.codes.ok:
            raise RuntimeError("Failed to register schema")

        return True

    def get_schemas(self, filter_name=None):
        """
        Retrieve the list of all available schemas in cluster.
        :param filter_name: optional search by name param
        :return: A schema collection
        :rtype: SchemaCollection
        """
        response = requests.get(self._get_url(self._SCHEMA_URI),
                                headers=self._get_headers())
        return SchemaCollection(response.json())

    def send(self, channel, data):
        """
        Send data to your data-api node and use the schema_id
        to convert data to an avro record from predefined schema
        :param channel: Channel name that will hold the sent data
        :param schema_id: a numeric ID provided with the schema
        :param data: a dict containing the data you're sending
        :return: response result
        :rtype: boolean
        """
        response = requests.post(
            '%s/%s/%s' % (self._api_url,
                          self._CHANNELS_URI,
                          channel),
            headers=self._get_headers(),
            json=data
        )

        if response.status_code == requests.codes.created:
            return True

        raise RuntimeError(response.text)

    def _get_headers(self):
        """
        Returns the HTTP request headers
        :return: A dictionary of headers
        :rtype: dict
        """
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-Auth-Token': self._api_token
        }

    def _get_url(self, uri):
        """
        Constructs the full URL of a request
        :param uri: The required URI
        :return: The full URL
        :rtype: string
        """
        return '/'.join([self._api_url, uri])
