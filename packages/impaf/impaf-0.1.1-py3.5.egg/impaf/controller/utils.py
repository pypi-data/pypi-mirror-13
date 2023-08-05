from pyramid.httpexceptions import HTTPFound

from .exceptions import QuitController


class ControllerUtils(object):

    def redirect(self, to, quit=False, **kwargs):
        url = self.request.route_url(to, **kwargs)
        self.response = HTTPFound(
            location=url,
            headers=self.request.response.headerlist,
        )
        if quit:
            raise QuitController(self.response)

    def add_widget(self, name, obj):
        obj.feed_request(self.request)
        self.context[name] = obj
