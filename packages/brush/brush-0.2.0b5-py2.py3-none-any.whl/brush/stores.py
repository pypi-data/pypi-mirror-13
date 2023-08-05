from collections import deque


class Store(object):
    """In-memory storage of recent data. A global instance is
    available as ``brush.stores.store``.

    :param int maxlen: Maximum number of points to store

    .. todo:: Implement a redis-backed version

    """
    def __init__(self, maxlen=60):
        self._data = deque(maxlen=maxlen)

    def append(self, data):
        """Append data to the store. The oldest data item will be
        removed if appending results in exceeding the maximum
        length.

        """
        self._data.append(data)

    def __getitem__(self, key):
        return self._data[key]

    def __iter__(self):
        return self._data.__iter__()


store = Store()


if __name__ == "__main__":
    store = Store()
    for x in range(10):
        store.append(x)

    for item in store:
        print(item)
