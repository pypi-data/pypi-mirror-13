from ..utils import cached


class ExampleCached(object):

    def __init__(self):
        self._cache = {}
        self.runned = 0

    @cached
    def counting(self):
        self.runned += 1
        return self.runned


class TestCached(object):

    def test_simple(self):
        obj = ExampleCached()

        assert obj.counting() == 1
        assert obj.counting() == 1
