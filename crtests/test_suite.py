""" How to test a todo?

This Module includes the test suite that verifies the todo component using
a black box methodology.

"""
from bbtest.testcase import BBTestCase

from crboxes.nodes import Endpoint, Host
from crboxes.servers import Transparency, Registry


class CRTestCase(BBTestCase):
    pass


class LabTest(CRTestCase):

    LAB = {
        'ep': {
            'box': Endpoint,
            'image': "linux",
            'boxes': [],
         },
        'server': {
            'box': Host,
            'image': "linux",
            'boxes': [Transparency, Registry],
         },
    }

    def test_add(self):
        todo_box = self.boxes['todo']
        todo_box.add("Foo")
        todos = todo_box.list()
        assert todos == ["Foo"]
