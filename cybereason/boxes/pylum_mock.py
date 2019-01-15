import os
import pickle
import subprocess

import unittest
from bbtest import HomeBox, BBTestCase

class MessageNotReceived(Exception):
    pass

#===============================================================================
# Common-data tuple offsets
#===============================================================================
SOURCE_OFFSET =     0
TYPE_OFFSET =       1
TIMESTAMP_OFFSET =  2
DATA_OFFSET =       3
# Filtering functions
def isSource(item, source):
    return source.lower() in item[SOURCE_OFFSET].lower()

def isType(item, type):
    return type.lower() in item[TYPE_OFFSET].lower()

def isBefore(item, timestamp):
    return item[TIMESTAMP_OFFSET] < timestamp

def isAfter(item, timestamp):
    return item[TIMESTAMP_OFFSET] > timestamp

class ANY_VALUE(object):
    def __str__(self):
        return "ANY_VALUE"
    __repr__ = __str__

class NOT_EXIST(object):
    def __str__(self):
        return "NOT_EXIST"
    __repr__ = __str__

class ALMOST_EQUAL(object):
    def __init__(self, value, delta):
        self.value = value
        self.delta = delta
    def __cmp__(self, other):
        if other-self.delta <= self.value <= other+self.delta:
            return 0
        else:
            return cmp(self.value, other)
    def __str__(self):
        return "ALMOST_EQUAL(%s, %s)"%(self.value, self.delta)
    __repr__ = __str__

class GREATER_OR_EQUAL(object):
    def __init__(self, value):
        self.value = value
    def __cmp__(self, other):
        return cmp(self.value, other) > 0
    def __str__(self):
        return "GREATER_OR_EQUAL(%s)"%(self.value)
    __repr__ = __str__

class NOT_EQUAL(object):
    def __init__(self, value):
        self.value = value
    def __cmp__(self, other):
        return not cmp(self.value, other)
    def __str__(self):
        return "NOT_EQUAL(%s)"%(self.value)
    __repr__ = __str__

class CONTAINS(object):
    def __init__(self, value):
        self.value = value
    def __cmp__(self, other):
        return 0 if self.value in other else 1
    def __str__(self):
        return "CONTAINS(%s)"%(self.value)
    __repr__ = __str__

class IN_LIST(object):
    def __init__(self, list):
        self.list = list
    def __contains__(self, other):
        self.other = other
        return self.other in self.list
    def __str__(self):
        return "IN_LIST(%s)"%( self.list)
    __repr__ = __str__

def inData(major, minor):
    for k,v in list(minor.items()):
        if v is NOT_EXIST:
            return k not in major
        if k not in major:
            return False
        if v is None or v is ANY_VALUE:
            continue
        if type(v) == dict:
            if not inData(major[k], v):
                return False
        elif type(v) == list:
            found = []
            for originalItem in major[k]:
                for requestedItem in v:
                    found.append(inData(originalItem, requestedItem))
            if not any(found):
                return False
        elif type(v) is IN_LIST:
            if type(major[k]) == list:
                for originalItem in major[k]:
                    for requestedItem in v.list:
                        if inData(originalItem, requestedItem):
                            return True
                return False
            elif major[k] not in v.list:
                return False
        elif type(v) is NOT_EQUAL:
            if major[k] != v:
                return False
        elif type(v) is GREATER_OR_EQUAL:
            if major[k] != v:
                return False
        elif type(v) is CONTAINS:
            if major[k] != v:
                return False
        else:
            if major[k] != v:
                return False
    return True

def isItem(item, source=None, type=None, timestamp=None, data={}):
    if source is not None and not isSource(item, source):
        return False
    if type is not None and not isType(item, type):
        return False
    if timestamp is not None and isBefore(item, timestamp):
        return False
    if not inData(item[DATA_OFFSET], data):
        return False
    return True

def filterItems(items, source=None, type=None, timestamp=None, data={}):
    for item in items:
        if isItem(item, source, type, timestamp, data):
            yield item

class DataSource(object):
    def __init__(self, name):
        self.name = name

class DataReader(DataSource):
    cache = None
    SIZED_PICKLE_HEADER_SIZE = 64

    def __init__(self, filename):
        super().__init__(os.path.splitext(spkl_filename)[0])
        self.fp = open(filename, "rb")
        self.size = pickle.loads(self.fp.read(self.SIZED_PICKLE_HEADER_SIZE))
        self.spkl_filename = spkl_filename
        if not os.path.isfile(spkl_filename):
            raise FileNotFoundErrorf(f"Data file {spkl_filename} does not exist")
        self.size = SizedPickledReader(self.spkl_filename).size

    def read(self):
        if not self.cache:
            self.cache = pickle.load(self.fp)
        return self.cache

    def filter(self, **kwargs):
        return list(filterItems(self.read(), **kwargs))



class Py2Box(HomeBox):
    def install(self, package_path):
        basename = os.path.basename(package_path)
        super().install()
        self.run('pip3', 'install', 'pipenv')
        self.put(package_path, basename)
        self.run('tar', '-xf', basename)
        self.run('pipenv', 'install', env={'PIPENV_IGNORE_VIRTUALENVS': '1'})

class TransparencyMockBox(Py2Box):

    # PACKAGEPATH = r'c:\Users\benny.daon\Source\pylum-mock\pylum-mock.tar'
    PACKAGEPATH = '/tmp/pylum-mock.tar'

    def install(self, port=8001):
        super().install(self.PACKAGEPATH)
        self.port = port
        self.proc = self.host.modules.subprocess.Popen(
            ['python3', '-m', 'pipenv','run', 'py', '-2', './server.py', '-v', '-p', str(port)],
            stdout=subprocess.PIPE, env={'PIPENV_IGNORE_VIRTUALENVS': '1'})

    def clean(self):
        #TODO: remove the sized pickled file

        pass

    @staticmethod
    def _find_message(filename, **kwargs):
        file_path = os.path.join(self.path, 'data', f'{filename}.spkl')
        data = DataReader(file_path)
        return data.filter(**kwargs)

    def assert_message_received(self, filename='AP', **kwargs):
        if not self.host.modules.TransparencyMockBox._find_message(filename, **kwargs):
            raise MessageNotReceived(f"Message like '{kwargs}' was not found")
