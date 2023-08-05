from pytest import fixture, yield_fixture
from mock import MagicMock, patch

from ..application import Application


class ExampleApplication(Application):

    def __init__(self, module, settings_factory):
        super().__init__(module)
        self._settings_factory = settings_factory

    def _generate_settings(self, settings, endpoint):
        super()._generate_settings(settings, endpoint, self._settings_factory)


class TestApplication(object):

    @fixture
    def app(self, mSettingsFactory):
        return ExampleApplication('module', mSettingsFactory)

    @fixture
    def mSettingsFactory(self):
        return MagicMock()

    @yield_fixture
    def mConfigurator(self, app):
        patcher = patch('impaf.application.Configurator')
        with patcher as mock:
            yield mock

    @yield_fixture
    def m_create_app(self, app):
        patcher = patch.object(app, '_create_app')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mimport_module(self):
        patcher = patch('impaf.application.import_module')
        with patcher as mock:
            yield mock

    def test_create_app(
        self,
        app,
        mSettingsFactory,
        mConfigurator,
        mimport_module,
    ):
        '''
        ._create_app should:
            - generate settings
            - create pyramid.config.Configurator
            - populate Configurator.registry
            - create routes
        '''
        get_for = mSettingsFactory.return_value.get_for
        settings = MagicMock()
        paths = MagicMock()
        get_for.return_value = (settings, paths)
        mConfigurator.return_value.registry = {}
        mimport_module.return_value.__file__ = 'path'

        app._create_app({'base': 'settings'}, 'uwsgi')

        mimport_module.assert_called_once_with('module')
        assert app.settings == settings
        assert app.paths == paths
        mConfigurator.assert_called_once_with(
            settings=settings.to_dict.return_value,
        )
        assert app.config == mConfigurator.return_value
        assert mConfigurator.return_value.registry == {
            'settings': settings,
            'paths': paths,
        }

    def test_run_uwsgi(self, app, m_create_app):
        '''
        run_uwsgi should create wsgi app
        '''
        app.config = MagicMock()

        result = app({'base': 'settings'})
        assert result == app.config.make_wsgi_app.return_value
        m_create_app.assert_called_once_with({'base': 'settings'}, 'uwsgi')

    def test_run_tests(self, app, m_create_app):
        app.run_tests({'base': 'settings'})
        m_create_app.assert_called_once_with({'base': 'settings'}, 'tests')

    def test_run_shell(self, app, m_create_app):
        app.run_shell({'base': 'settings'})
        m_create_app.assert_called_once_with({'base': 'settings'}, 'shell')

    def test_run_command(self, app, m_create_app):
        app.run_command({'base': 'settings'})
        m_create_app.assert_called_once_with({'base': 'settings'}, 'command')
