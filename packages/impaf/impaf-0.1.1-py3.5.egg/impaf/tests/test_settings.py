from pytest import fixture, yield_fixture
from mock import patch

from ..settings import SettingsFactory


class TestSettingsFactory(object):

    @fixture
    def factory(self):
        return SettingsFactory('mymodule', {'base': 'settings'})

    @yield_fixture
    def mFactory(self):
        patcher = patch('impaf.settings.Factory')
        with patcher as mock:
            mock.return_value.make_settings.return_value = (
                {'one': 1},
                {'two': 2},
            )
            yield mock

    def test_for_uwsgi(self, factory, mFactory):
        self._assert_factory(
            factory,
            mFactory,
            'uwsgi',
            [('local', False)],
        )

    def test_for_tests(self, factory, mFactory):
        self._assert_factory(
            factory,
            mFactory,
            'tests',
            [('tests', False)],
        )

    def test_for_shell(self, factory, mFactory):
        self._assert_factory(
            factory,
            mFactory,
            'shell',
            [('shell', False), ('local_shell', False)],
        )

    def test_for_command(self, factory, mFactory):
        self._assert_factory(
            factory,
            mFactory,
            'command',
            [('command', False), ('local_command', False)],
        )

    def _assert_factory(self, factory, mFactory, endpoint, modules):
        assert factory.get_for(endpoint) == (
            {'one': 1, 'paths': {'two': 2}},
            {'two': 2},
        )
        mFactory.assert_called_once_with('mymodule')

        external_factory = mFactory.return_value
        external_factory.make_settings(
            settings=factory.settings,
            additional_modules=modules,
        )
