from collections import defaultdict

from mock import MagicMock
from mock import patch
from mock import sentinel
from pytest import fixture
from pytest import yield_fixture
from pytest import raises

from .. import Controller
from ..exceptions import FinalizeController
from ..exceptions import QuitController


class ExampleController(Controller):

    def run(self):
        self.runned = defaultdict(lambda: False)
        return super().run()

    def _before_context(self):
        super()._before_context()
        self.runned['_before_context'] = True

    def _before_make(self):
        super()._before_make()
        self.runned['_before_make'] = True

    def _after_make(self):
        super()._after_make()
        self.runned['_after_make'] = True

    def _create_widgets(self):
        super()._create_widgets()
        self.runned['_create_widgets'] = True

    def _before_quit(self):
        super()._before_quit()
        self.runned['_before_quit'] = True

    def _get_request_cls(self):
        return lambda x: x


class ControllerFixtures(object):

    @fixture
    def mroot_factory(self):
        return MagicMock()

    @fixture
    def mrequest(self):
        return MagicMock()

    @fixture
    def controller(self, mroot_factory, mrequest):
        return ExampleController(mroot_factory, mrequest)

    @yield_fixture
    def mmake(self, controller):
        patcher = patch.object(controller, 'make')
        with patcher as mock:
            yield mock


class TestController(ControllerFixtures):

    def test_normaln_run(self, controller, mrequest, mroot_factory):
        response = controller()

        assert controller.context == {
            'request': mrequest,
            'route_path': mrequest.route_path,
        }
        assert controller.request == mrequest
        assert controller.root_factory == mroot_factory
        assert controller.response is None
        assert response == controller.context
        assert controller.runned == {
            '_before_context': True,
            '_before_make': True,
            '_after_make': True,
            '_create_widgets': True,
        }

    def test_on_response_setted(self, controller):
        """
        When .response on controller is not None, controller should return this
        response.
        """
        controller.response = sentinel.response

        assert controller() == sentinel.response

    def test_on_finalizing(self, controller, mrequest, mmake):
        """
        When .make raises FinalizeController, then all the rest of the
        controller mechanics should run normally. FinalizeController.context
        should be added to controller context.
        """
        mmake.side_effect = FinalizeController({'fin': True})

        assert controller() == {
            'request': mrequest,
            'route_path': mrequest.route_path,
            'fin': True,
        }

    def test_on_quit(self, controller, mmake):
        """
        QuitController should end up controller immediately and return whit
        what object was initalized.
        """
        mmake.side_effect = QuitController({'quit': True})

        assert controller() == {
            'quit': True,
        }
        assert controller.runned == {
            '_before_context': True,
            '_before_make': True,
            '_before_quit': True,
        }


class TestControllerUtils(ControllerFixtures):

    @yield_fixture
    def mHTTPFound(self):
        patcher = patch('impaf.controller.utils.HTTPFound')
        with patcher as mock:
            yield mock

    def test_add_widget(self, controller, mrequest):
        mwidget = MagicMock()
        controller.context = {}

        controller.add_widget('myname', mwidget)

        assert controller.context == {
            'myname': mwidget,
        }
        mwidget.feed_request.assert_called_once_with(mrequest)

    def test_redirect(self, controller, mrequest, mHTTPFound):
        controller.redirect('somewhere', kw='arg')

        assert controller.response == mHTTPFound.return_value
        mHTTPFound.assert_called_once_with(
            location=mrequest.route_url.return_value,
            headers=mrequest.response.headerlist,
        )
        mrequest.route_url.assert_called_once_with(
            'somewhere',
            kw='arg',
        )

    def test_redirect_with_quit(self, controller):
        with raises(QuitController):
            controller.redirect('somewhere', True, kw='arg')
