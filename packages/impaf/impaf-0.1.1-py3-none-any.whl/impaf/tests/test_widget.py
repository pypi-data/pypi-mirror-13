from mock import MagicMock
from pytest import fixture

from ..widget import Widget


class ExampleWidget(Widget):

    def __init__(self):
        super().__init__()
        self.mrequest = MagicMock()

    def _get_request_cls(self):
        return self.mrequest


class TestWidget(object):

    @fixture
    def mrequest(self):
        return MagicMock()

    @fixture
    def widget(self):
        return ExampleWidget()

    def test_feed_request(self, widget, mrequest):
        widget.feed_request(mrequest)

        widget.mrequest.assert_called_once_with(mrequest)
        assert widget.context == {
            'request': widget.mrequest.return_value,
            'widget': widget,
        }
