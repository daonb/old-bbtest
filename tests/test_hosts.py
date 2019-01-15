import unittest
from bbtest.hosts import LocalHost


class TestLocalHost(unittest.TestCase):
    def test_successful_run(self):
        host = LocalHost()
        self.assertTrue(host.run(['python', '--version'])[0].startswith('Python'))
