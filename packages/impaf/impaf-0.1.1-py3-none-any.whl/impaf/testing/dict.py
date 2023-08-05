from mock import MagicMock


class MockedDict(dict):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mock = MagicMock()

    def __getattr__(self, name):
        return getattr(self._mock, name)
