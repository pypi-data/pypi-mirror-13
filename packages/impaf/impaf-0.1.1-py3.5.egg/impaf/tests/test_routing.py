from pytest import fixture, yield_fixture
from mock import MagicMock, patch, sentinel
from tempfile import NamedTemporaryFile

from yaml import dump

from ..routing import RouteYamlParser, Routing


class TestRouteYamlParser(object):

    @fixture
    def parser(self):
        return RouteYamlParser('/highway/to/hell')

    @yield_fixture
    def mread_yaml(self, parser):
        patcher = patch.object(parser, 'read_yaml')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mparse_route_yaml(self, parser):
        patcher = patch.object(parser, '_parse_route_yaml')
        with patcher as mock:
            yield mock

    def test_parse(self, parser, mread_yaml, mparse_route_yaml):
        def example_generator(data):
            yield 10

        def side_effect():
            parser.data = sentinel.data

        mread_yaml.side_effect = side_effect
        mparse_route_yaml.side_effect = example_generator

        assert list(parser.parse()) == [10]
        mread_yaml.assert_called_once_with()
        mparse_route_yaml.assert_called_once_with(sentinel.data)

    def test_read_yaml(self, parser):
        tmp = NamedTemporaryFile(delete=False)
        tmp.write(
            bytes(
                dump(
                    {'mydata': 15}
                ),
                'utf8',
            )
        )
        tmp.close()

        parser.path = tmp.name
        parser.read_yaml()
        assert parser.data == {'mydata': 15}

    def test_parsing(self, parser):
        data = {
            'convent': {
                'controllers': [
                    {
                        'controller': 'ConventListController',
                        'route': 'convent:list',
                        'url': '/',
                    },
                    {
                        'controller': 'ConventEditController',
                        'route': 'convent:edit',
                        'url': '/edit',
                    },
                ]
            },
            'game': {
                'controllers': [
                    {
                        'controller': 'GameListController',
                        'route': 'game:list',
                        'url': '/g',
                    },
                    {
                        'controller': 'GameEditController',
                        'route': 'game:edit',
                        'url': '/g/edit',
                    },
                ]
            },
        }

        result = list(parser._parse_route_yaml(data))
        key_sorting = lambda x: x['controller']
        result.sort(key=key_sorting)

        assert result == sorted([
            {
                'controller': 'convent.controllers.ConventListController',
                'route': 'convent:list',
                'url': '/',
            },
            {
                'controller': 'convent.controllers.ConventEditController',
                'route': 'convent:edit',
                'url': '/edit',
            },
            {
                'controller': 'game.controllers.GameListController',
                'route': 'game:list',
                'url': '/g',
            },
            {
                'controller': 'game.controllers.GameEditController',
                'route': 'game:edit',
                'url': '/g/edit',
            },
        ], key=key_sorting)


class ExampleController(object):
    renderer = 'myrenderer'
    path_info = None


class TestRouting(object):

    @fixture
    def mapp(self):
        return MagicMock()

    @fixture
    def routing(self, mapp):
        return Routing(mapp)

    @yield_fixture
    def mRouteYamlParser(self):
        patcher = patch('impaf.routing.RouteYamlParser')
        with patcher as mock:
            yield mock

    @fixture
    def mconfig(self, mapp):
        return mapp.config

    @fixture
    def mpaths(self, mapp):
        return mapp.paths

    @yield_fixture
    def madd(self, routing):
        patcher = patch.object(routing, 'add')
        with patcher as mock:
            yield mock

    @yield_fixture
    def madd_view(self, routing):
        patcher = patch.object(routing, 'add_view')
        with patcher as mock:
            yield mock

    @yield_fixture
    def mread_from_file(self, routing):
        patcher = patch.object(routing, 'read_from_file')
        with patcher as mock:
            yield mock

    def test_read_from_file(self, routing, mRouteYamlParser, madd):
        """
        .read_from_file should parse yaml file and add routes from it
        """
        mroute = {'controller': 'something'}
        mRouteYamlParser.return_value.parse.return_value = [mroute]

        routing.read_from_file(sentinel.pathtofile)

        madd.assert_called_once_with(**mroute)
        mRouteYamlParser.assert_called_once_with(sentinel.pathtofile)
        mRouteYamlParser.return_value.parse.assert_called_once_with()

    def test_add(self, routing, mconfig, madd_view):
        routing.add('controller', 'route', 'url', 'arg', kw='arg')

        mconfig.add_route('route', 'url', 'arg', kw='arg')
        madd_view.assert_called_once_with('controller', route_name='route')

    def test_add_view(self, routing, mconfig):
        mconfig.maybe_dotted.return_value = ExampleController
        routing.add_view(
            'impaf.tests.test_routing.ExampleController',
            route_name='something',
        )

        mconfig.add_view(
            'impaf.tests.test_routing.ExampleController',
            route_name='something',
            renderer='myrenderer',
        )

    def test_read_from_dotted(self, routing, mpaths, mread_from_file):
        routing.read_from_dotted('my.dotted.path')

        mpaths.get_path_dotted.assert_called_once_with('my.dotted.path')
        mread_from_file.assert_called_once_with(
            mpaths.get_path_dotted.return_value
        )
