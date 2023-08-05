import sys

SESSION_CACHE = {}


def cache(method='test'):

    if hasattr(method, '__call__'):
        fun = method
        method = 'test'
    else:
        fun = None

    def choose_method(fun):
        name = fun.__name__

        def test(self, *args, **kwargs):
            key = [self] + list(args) + sorted(kwargs.items())
            cache_key = name + str(key)

            try:
                cache = self._instant_cache
            except AttributeError:
                cache = self._instant_cache = {}

            if cache_key not in cache:
                cache[cache_key] = fun(self, *args, **kwargs)

            return cache[cache_key]

        def instance(self, *args, **kwargs):
            key = list(args) + sorted(kwargs.items())
            cache_key = name + str(key)

            try:
                cache = self._instant_cache
            except AttributeError:
                cache = self._instant_cache = {}

            if cache_key not in cache:
                cache[cache_key] = fun(self, *args, **kwargs)
            return cache[cache_key]

        def module(self, *args, **kwargs):
            key = list(args) + sorted(kwargs.items())
            cache_key = name + str(key)

            module = sys.modules[self.__module__]
            cache = getattr(module, '_module_cache', {})
            setattr(module, '_module_cache', cache)
            if cache_key not in cache:
                cache[cache_key] = fun(self, *args, **kwargs)
            return cache[cache_key]

        def session(self, *args, **kwargs):
            key = list(args) + sorted(kwargs.items())
            cache_key = name + str(key)

            cache = SESSION_CACHE
            if cache_key not in cache:
                cache[cache_key] = fun(self, *args, **kwargs)
            return cache[cache_key]

        return locals()[method]

    if fun:
        return choose_method(fun)
    else:
        return choose_method
