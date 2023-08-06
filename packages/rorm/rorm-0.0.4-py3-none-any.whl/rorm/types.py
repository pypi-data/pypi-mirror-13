import redis
import uuid
import collections

from .client import Client


class RedisDataType:
    def __init__(self, *args, key=None, **kwargs):
        self._client = Client.get_client()
        self._key = self._prepare_key(key)

    @property
    def key(self):
        return self._key

    @staticmethod
    def _prepare_key(key):
        return key if key else uuid.uuid4().hex


class Hash(RedisDataType, collections.MutableMapping):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if data:
            try:
                data = dict(data)
            except (TypeError, ValueError) as e:
                raise ValueError(
                    "'data' argument must be iterable sequence of "
                    "2-element tuple, dict, zip or None. ") from e
            else:
                self._client.hmset(self._key, data)

    def __getitem__(self, key):
        value = self._client.hget(self._key, key)
        if value is None:
            raise KeyError(key)
        return value

    def __setitem__(self, key, value):
        return self._client.hset(self._key, key, value)

    def __delitem__(self, key):
        return self._client.hdel(self._key, key)

    def __iter__(self):
        return iter(self._client.hkeys(self._key))

    def __len__(self):
        return self._client.hlen(self._key)

    def __str__(self):
        return str(self.items(as_dict=True))

    def keys(self):
        return self._client.hkeys(self._key)

    def values(self):
        return self._client.hvals(self._key)

    def items(self, as_dict=False):
        items = self._client.hgetall(self._key)
        if as_dict:
            return items
        return tuple(zip(items.keys(), items.values()))


class Sequence(RedisDataType, collections.Sequence):

    def _get(self):
        """
        Returns whole sequence
        """
        raise NotImplementedError

    def _get_ranges(self, index):
        """
        Returns counterparts of ranges for redis '*range' method.
        """
        data_length = len(self)

        if not isinstance(index, slice):
            if not isinstance(index, int):
                raise TypeError('string indices must be integers')
            if -index > data_length or index >= data_length:
                raise IndexError('string index out of range')
            index = slice(index, index+1 or None, None)

        start, stop, step = index.start, index.stop, index.step

        step = 1 if step is None else step
        start = 0 if start is None else start
        if stop is None:
            stop = len(self) - 1
        elif stop == 0 or stop <= -len(self):
            start = -1
            stop = 0
        else:
            stop = stop - 1

        if step < 0:
            raise IndexError(
                'step indice must be positive integer'
            ) from NotImplementedError

        return start, stop, step

    def __contains__(self, value):
        return value in self._get()

    def __getitem__(self, index):
        return NotImplementedError

    def __str__(self):
        return str(self._get())

    def __len__(self):
        return NotImplementedError

    def index(self, value, start=0, stop=None):
        '''S.index(value, [start, [stop]]) -> integer -- return first index of value.
           Raises ValueError if the value is not present.
        '''

        # this is a modified copy of _collections_abc.Sequence.index
        # the orginal lacks for handling slice indices

        if start is not None and start < 0:
            start = max(len(self) + start, 0)
        if stop is not None and stop < 0:
            stop += len(self)

        i = start
        while (stop is None or i < stop) and i < len(self):
            try:
                if self[i:i+len(value)] == value:
                    return i
            except IndexError:
                break
            i += 1
        raise ValueError('substring not found')

    def count(self, value):
        return self._get().count(value)


class MutableSequence(Sequence, collections.MutableSequence):
    pass


class String(Sequence):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        data and self._client.set(self._key, data)

    def __getitem__(self, *args, **kwargs):
        try:
            start, stop, step = self._get_ranges(*args, **kwargs)
        except IndexError:
            # TODO: OPTIMIZE ITEM GET WITH NEGATIVE STEP INDICE
            result = self._get()
            return result.__getitem__(*args, **kwargs)
        return self._client.getrange(self._key, start, stop)[::step]

    def __len__(self):
        return self._client.strlen(self._key)

    def _get(self):
        return self._client.get(self._key)


class List(MutableSequence):
    def __init__(self, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if data:
            if isinstance(data, (list, tuple)):
                raise ValueError("{} argument must be list or tuple".format(data))
            self._client.lpush(self._key, *data)

    def __getitem__(self, *args, **kwargs):
        start, stop, *_ = super().__getitem__(*args, **kwargs)
        value = self._client.lrange(self._key, start, stop)
        return value

    def __setitem__(self, index, value):
        if not isinstance(index, int):
            # FIXME more verbose error mesage
            raise IndexError
        return self._client.lset(self._key, index, value)

    def __len__(self):
        return self._client.llen(self._key)

    def __delitem__(self, index):
        pivot = uuid.uuid4().hex
        self._client.lset(self._key, index, pivot)
        return self._client.lrem(self._key, pivot, 1)  # andymccurdy/redis-py #145, #162 -- reversed order of the parameters

    def insert(self, index, value):
        pivot = uuid.uuid4().hex
        value_after = self[index][0].decode()
        self[index] = pivot
        self._client.linsert(self._key, 'AFTER', pivot, value_after)
        result = self._client.linsert(self._key, 'BEFORE', pivot, value)
        self._client.lrem(self._key, pivot, 1)
        return result
