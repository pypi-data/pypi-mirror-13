class QuitController(Exception):
    """
    Immediately ends controller. Controller will return provided response.
    """

    def __init__(self, response=None):
        self.response = response


class FinalizeController(Exception):
    """
    Ends .make method. Other Controller mechanics will work normally.
    """

    def __init__(self, context=None):
        self.context = context or {}
