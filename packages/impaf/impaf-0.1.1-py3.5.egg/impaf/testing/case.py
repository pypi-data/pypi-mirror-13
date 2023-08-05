from mock import patch
from mock import MagicMock
from pytest import fixture

from .cache import cache
from .dict import MockedDict


class TestCase(object):

    _object_cls = None

    def setUp(self):
        self._test_cache = {}
        self._patchers = []

    def tearDown(self):
        for patch in self._patchers:
            patch.stop()

    def patch(self, *args, **kwargs):
        patcher = patch(*args, **kwargs)
        self._patchers.append(patcher)
        return patcher.start()

    def pobject(self, *args, **kwargs):
        patcher = patch.object(*args, **kwargs)
        self._patchers.append(patcher)
        return patcher.start()

    def pdict(self, *args, **kwargs):
        patcher = patch.dict(*args, **kwargs)
        self._patchers.append(patcher)
        return patcher.start()

    @cache
    def object(self, *args, **kwargs):
        return self._object_cls(*args, **kwargs)


class PyTestCase(TestCase):

    @fixture(autouse=True)
    def pytest_setup(self, request):
        self.setUp()
        request.addfinalizer(self.tearDown)


class RequestCase(TestCase):

    @cache
    def mrequest(self):
        return MagicMock()

    @cache
    def mregistry(self):
        self.mrequest().registry = MockedDict({
            'settings': {},
            'paths': {},
        })
        return self.mrequest().registry

    @cache
    def mPOST(self):
        self.mrequest().POST = MockedDict({})
        return self.mrequest().POST

    @cache
    def mGET(self):
        self.mrequest().GET = MockedDict({})
        return self.mrequest().GET

    @cache
    def mmatchdict(self):
        self.mrequest().matchdict = MockedDict({})
        return self.mrequest().matchdict

    @cache
    def mroute_path(self):
        return self.mrequest().route_path

    @cache
    def msettings(self,):
        return self.registry()['settings']

    @cache
    def mpaths(self):
        return self.registry()['paths']


class ControllerCase(RequestCase):

    @cache
    def mroot_factory(self):
        return MagicMock()

    @cache
    def context(self):
        return {}

    @cache
    def matchdict(self):
        self.mrequest().matchdict = {}
        return self.mrequest().matchdict

    @cache
    def object(self):
        cls = self._object_cls
        self._prepere_controller_cls(cls)
        return self._prepere_testable(
            cls,
            self.mroot_factory(),
            self.mrequest(),
            self.context(),
        )

    def _prepere_controller_cls(self, cls):
        def set_request(self, request):
            self.request = request
        cls._convert_request = set_request

    def _prepere_testable(self, cls, mroot_factory, mrequest, context):
        obj = cls(mroot_factory, mrequest)
        obj.context = context
        return obj

    @cache
    def mredirect(self):
        return self.pobject(self.object(), 'redirect')

    @cache
    def madd_widget(self):
        return self.pobject(
            self.object(),
            'add_widget',
        )
