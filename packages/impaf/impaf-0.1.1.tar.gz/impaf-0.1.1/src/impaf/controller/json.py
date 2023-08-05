from .base import Controller


class JsonController(Controller):
    """
    Controller which will return context as json.
    """
    renderer = 'json'

    def _create_context(self):
        self.context = {}
