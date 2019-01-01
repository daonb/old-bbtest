"""
Hosts in the network.
"""
import os
import platform
import subprocess
import shutil
import tempfile
from winreg import HKEY_LOCAL_MACHINE, OpenKey, EnumKey, QueryValueEx
from ftplib import FTP
import rpyc
import winrm

import psutil
from psutil import NoSuchProcess


class BaseHost(object):
    """"A base host class

    :param SEP: The path separator character
    :type SEP: str

    """
    SEP = '/'

    @property
    def os(self):
        raise NotImplementedError('Missing method implmentation')

    @property
    def bit(self):
        raise NotImplementedError('Missing method implmentation')

    @property
    def package_type(self):
        raise NotImplementedError('Non Windows OS')

    def destroy(self):
        """Release the host"""
        raise NotImplementedError('Missing method implmentation')

    def uninstall(self):
        """ the opposite of install,  uninstall our tools from the host """
        raise NotImplementedError('Missing method implmentation')

    def clean(self):
        raise NotImplementedError('Missing method implmentation')

    def isfile(self, path):
        raise NotImplementedError('Missing method implmentation')

    def rmtree(self, path, ignore_errors=True, onerror=None):
        raise NotImplementedError('Missing method implmentation')

    def rmfile(self, path):
        raise NotImplementedError('Missing method implmentation')

    def join(self, *args):
        return self.SEP.join(args)

class LocalHost(BaseHost):
    """Suppose to be an os-agnostic local host.

    For now, supports only Win32 and Win64
    """
    def __init__(self):
        super().__init__()
        try:
            self.root_path = self.ROOT_PATH
        except AttributeError:
            self.root_path = tempfile.gettempdir()

    @property
    def os(self):
        """Returns a lower case string identifying the OS"""
        return platform.platform().lower()

    @property
    def bit(self):
        #TODO: use a regex to extract 23|64
        return platform.architecture()[0][0:2]

    @property
    def package_type(self):
        raise NotImplementedError('Non Windows OS')

    def run(self, cmd, *args, **kwargs):
        args_list = list(args) if args else []
        output = subprocess.run(
            [cmd] + args_list, stdout=subprocess.PIPE, **kwargs)
        return output.stdout.decode('utf-8').strip().split('\n') if output.stdout else []

    def put(self, local, remote):
        return shutil.copyfile(local, remote)

    def mkdtemp(self, **kwargs):
        """ same args as tempfile.mkdtemp """
        return tempfile.mkdtemp(**kwargs)

    def rmtree(self, path, ignore_errors=True, onerror=None):
        return shutil.rmtree(path, ignore_errors, onerror)

    def rmfile(self, path):
        try:
            os.remove(path)
        except OSError:
            pass

    def rmfiles(self, path):
        try:
            for root, dirs, files in os.walk(path):
                for file in files:
                    os.remove(os.path.join(root, file))
                for dir in dirs:
                    self.rmtree(os.path.join(root, dir))
        except OSError:
            pass

    def isfile(self, path):
        return os.path.isfile(path)

    def run_python2(self, *args, **kwargs):
        if 'win' in self.os.lower():
            python_executable = ['py', '-2']
        else:
            python_executable = ['python2']
        return self.run(*python_executable, *args, **kwargs)

    @staticmethod
    def is_process_running(process_name):
        for process in psutil.process_iter():
            if process.name() == process_name:
                return True
        return False

class LocalWindowHost(LocalHost):
    """A collection of windows utilities and validators """
    ROOT_PATH = 'c:/temp'
    package_type = 'msi'

    @staticmethod
    def is_package_installed(name):
        key_val = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall'
        products = OpenKey(HKEY_LOCAL_MACHINE, key_val)
        try:
            i = 0
            while True:
                product_key_name = EnumKey(products, i)
                product_values = OpenKey(products, product_key_name)
                try:
                    if QueryValueEx(product_values, 'DisplayName')[0] == name:
                        return True
                except FileNotFoundError:
                    # product has no 'DisplayName' attribute
                    pass
                i = i+1
        except WindowsError:
            return False

    @staticmethod
    def is_service_running(service_name):
        try:
            return psutil.win_service_get(service_name).status() == 'running'
        except NoSuchProcess:
            return False

    @staticmethod
    def mkdtemp(**kwargs):
        return tempfile.mkdtemp(**kwargs)


class RemoteHost(BaseHost):
    """A remote host using RPyC
    """
    def __init__(self, ip=None, auth=None):
        self.ip = ip
        self.auth = auth
        self.ftp = FTP(ip)
        self.ftp.login()
        self._rpyc = rpyc.classic.connect("localhost")
        self.modules = self._rpyc.modules

    def mkdtemp(self, **kwargs):
        """ same args as tempfile.mkdtemp """
        return self.modules.tempfile.mkdtemp()

    def isfile(self, path):
        return self.modules.os.path.isfile(path)

    def run(self, cmd, *args, **kwargs):
        """ Run any CLI command.

        :todo implement over winrm and ssh.
        :param cmd:
        :param args:
        :param kwargs:
        :return:
        """
        args_list = list(args) if args else []
        if isinstance(self, WindowsHost):
            output = self.winrm.run_cmd(cmd, args_list)
            ret = output.std_out.decode('utf-8').strip().split('\n')
        else:
            #TODO: use ssh
            raise NotImplementedError("Run still doesn't work on Linux")

        return ret

    def run_python2(self, *args, **kwargs):
        """Call run command with python2 as the process"""
        pass

    def put(self, local, remote):
        ftp_remote = remote.replace('\\', '/')[len(self.root_path):]
        self.ftp.storbinary(f'STOR {ftp_remote}', open(local, 'rb'))


class WindowsHost(RemoteHost):
    """ A remote windows host """

    def __init__(self, ip="localhost", auth=("user", "pass")):
        super().__init__(ip, auth)
        self.winrm = winrm.Session(ip, auth=auth, transport='ntlm')

    def is_service_running(self, service_name):
        try:
            return self.modules.psutil.win_service_get(service_name).status() == 'running'
        except NoSuchProcess:
            return False

    def is_package_installed(self, name):
        return self.modules.bbtest.LocalWindowsHost.is_package_installed(name)

    def mkdtemp(self, **kwargs):
        """ same args as tempfile.mkdtemp """
        if not 'dir' in kwargs:
            kwargs['dir'] = self.root_path
        return self.modules.bbtest.LocalWindowsHost.mkdtemp(**kwargs)

class LinuxHost(RemoteHost):
    pass


class OSXHost(RemoteHost):
    pass
