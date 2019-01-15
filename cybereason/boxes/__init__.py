
from bbtest.blackboxes import HomeBox
from .pylum_mock import TransparencyMockBox

__all__ = ['CRBox', 'TransparencyMockBox']


class CRBox(HomeBox):
    """Base box for all Cybereason boxes.
    """

    def __init__(self, host, name=None):
        self.__class__.NAME = self.__class__.__name__[:-3].lower()
        super().__init__(host, name=name)
