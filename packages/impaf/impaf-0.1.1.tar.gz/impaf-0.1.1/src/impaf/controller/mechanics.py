from .exceptions import QuitController, FinalizeController
from impaf.requestable import Requestable


class ControllerMechanics(Requestable):

    def __init__(self, root_factory, request):
        self.feed_request(request)
        self.root_factory = root_factory
        self.response = None

    def __call__(self):
        return self.run()

    def run(self):
        try:
            self._before_context()
            self._create_context()
            self._before_make()
            self._make()
            self._after_make()
            return self._get_response()
        except QuitController as end:
            self._before_quit()
            return end.response or self.response

    def _make(self):
        try:
            self.make()
        except FinalizeController as finalizer:
            self.context.update(finalizer.context)

    def _create_context(self):
        self.context = {
            'request': self.request,
            'route_path': self.request.route_path,
        }

    def make(self):
        pass

    def _get_response(self):
        if self.response is None:
            self._create_widgets()
            return self.context
        else:
            return self.response
