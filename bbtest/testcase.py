
from unittest import TestCase

from bbtest import BlackLab


class BBTestCase(TestCase):
    """A black box test case based on :class:`TestCase` """

    def setUp(self):
        """setups a lab for black box testing. """
        super().setUp()
        self.lab = BlackLab(self.LAB)
        # Most tests don't care about the lab and its topology so they should access boxes directly.
        self.boxes = self.lab.boxes

    def tearDown(self):
        self.lab.clean()
        super().tearDown()
