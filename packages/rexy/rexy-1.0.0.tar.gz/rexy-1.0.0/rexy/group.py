# coding:utf-8


class Group(object):
    def __init__(self, data):
        self._data = data

    def __iter__(self):
        return self._data.__iter__()

    def __contains__(self, key):
        return self._data.__contains__(key)

    def one(self, key):
        return self._data.get(key, [None])[0]

    def many(self, key):
        return self._data.get(key, [])
