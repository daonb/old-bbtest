"""
"""

from bbtest import BBTestCase
from bbtest import LinuxHost
from cybereason.boxes.sensor import SensorBox
from cybereason.boxes import TransparencyMockBox


class PylumMockTest(BBTestCase):

    LAB = {
        'host1': {
            'class': LinuxHost,
            'boxes': [TransparencyMockBox],
         },
    }
    address_book = {'host1': {'ip': '127.0.0.1', 'auth': ('bbtest', 'Password1')}}

    def test_install(self):
        """
        """
        box = self.lab.boxes[TransparencyMockBox.NAME][0]
        line = box.proc.stdout.read()
        assert line == "please fail"
