from pytest import fixture

from ..json import JsonController
from .test_controller import ControllerFixtures


class TestJsonController(ControllerFixtures):

    @fixture
    def controller(self, mroot_factory, mrequest):
        return JsonController(mroot_factory, mrequest)

    def test_normal_run(self, controller):
        assert controller() == {}
