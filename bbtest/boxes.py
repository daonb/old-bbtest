
from .labs import BlackLab


class BlackBox():
    """This is an abstract class used to wrap a component in a black box.
    Black boxes can then be used to test the component itself and to verify
    it integrates well with other components.
    A blackbox runs on a host and you can communicate with it using `host.run`
    """

    host = None

    def __init__(self, name=None):
        self.name = name if name else self.__class__.__name__[:-3].lower()

    def start(self):
        pass
