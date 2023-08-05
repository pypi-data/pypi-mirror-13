from mock import MagicMock
from mock import patch

from pytest import fixture
from pytest import yield_fixture

from .dict import MockedDict


class BaseFixture(object):

    @fixture
    def testable(self):
        return self._prepere_testable(self._testable_cls)

    _testable_cls = None

    def _prepere_testable(self, cls):
        return cls()


class RequestFixture(BaseFixture):

    @fixture
    def mrequest(self):
        return MagicMock()

    @fixture
    def registry(self, mrequest):
        mrequest.registry = MockedDict({
            'settings': {},
            'paths': {},
        })
        return mrequest.registry

    @fixture
    def POST(self, mrequest):
        mrequest.POST = MockedDict({})
        return mrequest.POST

    @fixture
    def GET(self, mrequest):
        mrequest.GET = MockedDict({})
        return mrequest.GET

    @fixture
    def matchdict(self, mrequest):
        mrequest.matchdict = MockedDict({})
        return mrequest.matchdict

    @fixture
    def mroute_path(self, mrequest):
        mrequest.route_path = MockedDict({})
        return mrequest.route_path

    @fixture
    def settings(self, registry):
        return registry['settings']

    @fixture
    def paths(self, registry):
        return registry['paths']


class ControllerFixture(RequestFixture):

    @fixture
    def mroot_factory(self):
        return MagicMock()

    @fixture
    def context(self):
        return {}

    @fixture
    def testable(self, mroot_factory, mrequest, context):
        cls = self._testable_cls
        self._prepere_controller_cls(cls)
        return self._prepere_testable(
            cls,
            mroot_factory,
            mrequest,
            context,
        )

    def _prepere_controller_cls(self, cls):
        def set_request(self, request):
            self.request = request
        cls._convert_request = set_request

    def _prepere_testable(self, cls, mroot_factory, mrequest, context):
        obj = cls(mroot_factory, mrequest)
        obj.context = context
        return obj

    @yield_fixture
    def mredirect(self, testable):
        patcher = patch.object(testable, 'redirect')
        with patcher as mock:
            yield mock

    @yield_fixture
    def madd_widget(self, testable):
        patcher = patch.object(testable, 'add_widget')
        with patcher as mock:
            yield mock
