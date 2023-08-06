# coding:utf-8


class cached(object):
    def __init__(self, f):
        self._f = f

    def __get__(self, instance, owner):
        if instance is None:
            return self

        else:
            if self._f.__name__ not in instance._cache:
                instance._cache[self._f.__name__] = self._f(instance)

            return instance._cache[self._f.__name__]

    def __set__(self, instance, value):
        raise AttributeError('cannot set attribute')

    def __delete__(self, instance):
        del instance._cache[self._f.__name__]
