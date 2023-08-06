import json


class ChannelCollection(object):
    def __init__(self, data):
        if not isinstance(data, list):
            raise ValueError('A list is required to form ChannelCollection')

        self._items = []
        for item in data:
            channel = Channel().from_dict(item)
            self._items.append(channel)

        self._iter_pos = -1

    def __iter__(self):
        return self

    def next(self):
        self._iter_pos += 1
        if self._iter_pos >= len(self._items):
            raise StopIteration()
        else:
            return self._items[self._iter_pos]

    def __str__(self):
        return '\n'.join([str(item) for item in self._items])


class Channel(object):
    def __init__(self):
        """
        Initialize the channel object with None values
        """
        self.name = None
        self.partitions = None

    def from_dict(self, data):
        """
        Transform a dictionary into a Channel object
        :param data: a dict of channel values
        """
        if not isinstance(data, dict):
            raise ValueError('Data should be a dictionary')

        self.name = data['name']
        self.partitions = []
        if 'partitions' in data and data['partitions']:
            for partition in data['partitions']:
                self.partitions.append(Partition().from_dict(partition))

        return self

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps({
            'name': self.name,
            'partitions': [parition.to_dict() for parition in self.partitions]
        }, indent=4)

    def __unicode__(self):
        return self.__str__()


class Partition(object):
    def __init__(self):
        """
        Initialize a partition with None values
        """
        self.id = None
        self.leader = None
        self.replicas = None
        self.isr = None

    def from_dict(self, data):
        """
        Transform a dictionary into a Channel object
        :param data: a dict of channel values
        """
        if not isinstance(data, dict):
            raise ValueError('Data should be a dictionary')

        for key, value in data.iteritems():
            if key == 'partitionId':
                key = 'id'
            setattr(self, key, value)

        return self

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        return json.dumps(self.__dict__, indent=4)

    def __unicode__(self):
        return self.__str__()
