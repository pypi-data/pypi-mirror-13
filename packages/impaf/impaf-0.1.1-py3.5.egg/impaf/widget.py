from .requestable import Requestable


class Widget(Requestable):

    def feed_request(self, request):
        super().feed_request(request)
        self._create_context()

    def _create_context(self):
        self.context = {
            'request': self.request,
            'widget': self,
        }

    def add_widget(self, name, obj):
        obj.feed_request(self.request)
        self.context[name] = obj
