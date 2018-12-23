"""
Hosts in the network.
"""
import os
import subprocess
import sys
import shutil
import tempfile


class BaseHost(object):
    _SEP = '/'

    def __init__(self, ip=None, username=None, password=None):
        self.ip = ip
        self.username = username
        self.password = password

    def install(self, downloads_dir, **kwargs):
        pass

    def uninstall(self):
        """ the opposite of install,  uninstall our tools from the host """
        pass

    def clean(self):
        pass

    def join(self, *args):
        return self._SEP.join(args)

    def mkdtemp(self, **kwargs):
        """ same args as tempfile.mkdtemp """
        pass

    def rm(self, path, recursive=False, force=False):
        pass

    def isfile(self, path):
        pass

    # TODO: remove the next methods as they are too specific
    def rmtree(self, path, ignore_errors=True, onerror=None):
        pass

    def rmfile(self, path):
        pass


class LocalHost(BaseHost):

    @property
    def os(self):
        return sys.platform

    def run(self, cmd, *args, **kwargs):
        args_list = list(args) if args else []
        output = subprocess.run(
            [cmd] + args_list, stdout=subprocess.PIPE, **kwargs)
        return output.stdout.decode('utf-8').strip().split('\n')

    def put(self, local, remote):
        return shutil.copyfile(local, remote)

    def mkdtemp(self, **kwargs):
        return tempfile.mkdtemp(**kwargs)

    def rm(self, path, recursive=False, force=False):
        options = list()
        if recursive:
            options.append('-r')
        if force:
            options.append('-f')
        options.append(path)
        return self.run('rm', *options)

    def rmtree(self, path, ignore_errors=True, onerror=None):
        return shutil.rmtree(path, ignore_errors, onerror)

    def rmfile(self, path):
        try:
            os.remove(path)
        except OSError:
            pass

    def isfile(self, path):
        return os.path.isfile(path)


class WindowsHost(BaseHost):

    @property
    def os(self):
        return 'win32'


class LinuxHost(BaseHost):

    @property
    def os(self):
        return 'linux'


class OSXHost(BaseHost):
    pass
