
from bbtest.blackboxes import HomeBox

__all__ = ['CRBox']


class CRBox(HomeBox):
    """Base box for all Cybereason boxes.
    """

    def __init__(self, host, name=None):
        self.__class__.NAME = self.__class__.__name__[:-3].lower()
        super().__init__(host, name=name)
