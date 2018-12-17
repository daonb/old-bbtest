"""
Hosts in the network.
"""
import os
import sys
from shutil import copyfile


class Host(object):
    def __init__(self, ip=None, username=None, password=None):
        self.ip = ip
        self.username = username
        self.password = password

    def install(self, downloads_dir, **kwargs):
        pass

class LocalHost(Host):

    @property
    def os(self):
        return sys.platform

    @property
    def temp_dir(self):
        if self.os == 'win32':
            return 'c:/temp'
        else:
            None

    def run(self, cmd):
        return os.system(cmd)

    def put(self, local, remote):
        return copyfile(local, remote)


class WindowsHost(Host):

    @property
    def os(self):
        return 'win32'


class LinuxHost(Host):
    pass


class MacHost(Host):
    pass
