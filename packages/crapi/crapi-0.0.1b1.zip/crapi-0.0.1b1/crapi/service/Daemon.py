# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the service module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
# Python native libraries.
import os
import sys
import time

import crapi.service.WindowsDaemonFactory as WindowsDaemonFactory
import crapi.ipc.ClientPipe as ClientPipe
import crapi.misc.Utils as Utils
from crapi.service.DaemonError import DaemonError
from crapi.service.DaemonTimeoutError import DaemonTimeoutError
from crapi.service.DaemonPrivilegeException import DaemonPrivilegeException

# Python 3rd party libraries.
if sys.platform.startswith('win'):
    import win32serviceutil as w32scu
    import win32service as w32svc
    import win32process as w32ps
    import win32event as w32ev
    import win32con as w32con
    import win32com.shell.shellcon as w32shcon
    import win32com.shell.shell as w32sh_sh
    import pywintypes as WinT
    import winerror as werr


# NOTE: SEE_MASK_NOASYNC = SEE_MASK_NOCLOSEPROCESS + SEE_MASK_FLAG_DDEWAIT
class Daemon(object):

    def __init__(
        self, name='crapi', display_name='CRAPI: Common Range API',
        description='Dynamic runtime templating engine of Daemon services.',
        timeout=0, setup_timeout=0, action_file='.', su_aware=True,
        venv_aware=True, venv_dir='.virtualenvs', venv_name='crapi'
    ):
        d_module, d_py_class = WindowsDaemonFactory.instantiate(
            name=name, display_name=display_name, description=description,
            timeout=timeout, action_file=action_file
        )

        self.name = name
        self.display_name = display_name
        self.description = description
        if timeout == 0:
            self.timeout = float('inf')
        else:
            self.timeout = timeout
        if setup_timeout == 0:
            self.setup_timeout = w32ev.INFINITE
        else:
            self.setup_timeout = setup_timeout
        self.module = d_module
        self.python_class = d_py_class

        # Mandatory if admin privileges are required!
        src_file_md = Utils.Environment.getSourceFileDir(
            name=__name__
        )
        # FIXME: If venv_aware deduce these from your own! :]
        py_bin_path = Utils.Environment.getPyVirtualEnv(
            folder=venv_dir, name=venv_name
        )

        # FIXME (critical): Check the registry that:
        #        HKLM\Software\Python\PythonService\<py_ver - such as 2.7> key
        #       is correctly set!
        # FIXME: If the service is already installed reload its signature via
        #        the registry.
        # FIXME: If the service is deleted from sc.exe then add this file to
        #        folder (i.e. removed - check rt folder).
        try:
            svc_codes = w32scu.QueryServiceStatus(name)
            if svc_codes[1] == w32svc.SERVICE_STOPPED:
                w32scu.StartService(serviceName=self.name)
                Daemon.start(name=self.name)
        except WinT.error, e:
            if e.args[0] == werr.ERROR_SERVICE_DOES_NOT_EXIST:
                cmd = (
                    src_file_md + os.sep + 'management' +
                    os.sep + 'Administrator.py' +
                    ' install ' + self.name +
                    ' "' + self.display_name + '"' +
                    ' "' + self.description + '" ' +
                    self.python_class
                )
                self.__install(
                    su_aware=su_aware, cmd=cmd, binary=py_bin_path
                )
        # NOTE: Don't use a finally blocs so as to inform user about wrongly
        #       registered virtualenv value in the registry hive
        #       HKLM\Software\Python\PythonService\<py_ver - such as 2.7> for
        #       pythonservice.exe!
        svc_codes = w32scu.QueryServiceStatus(self.name)
        if svc_codes[1] == w32svc.SERVICE_STOPPED:
            cmd = (
                src_file_md + os.sep + 'management' +
                os.sep + 'Administrator.py' +
                ' activate ' + self.name
            )
            self.__start(su_aware=su_aware, cmd=cmd, binary=py_bin_path)
        self.pipe = ClientPipe.ClientPipe(name=self.name)

    def __install(self, su_aware, cmd, binary):
        try:
            w32scu.InstallService(
                pythonClassString=self.python_class,
                serviceName=self.name,
                displayName=self.display_name,
                description=self.description,
                startType=w32svc.SERVICE_AUTO_START,
                delayedstart=True
            )
        except WinT.error, e:
            if e.args[0] == werr.ERROR_ACCESS_DENIED:
                if not su_aware:
                    raise DaemonPrivilegeException(
                        'Windows daemon service installation failed: '
                        'Administrator privileges are required!',
                        'ERROR_ACCESS_DENIED',
                        e.args[0]
                    )
                else:
                    self.__elevate(
                        binary=binary,
                        cmd=cmd,
                        timeout=self.setup_timeout
                    )

    def __start(self, su_aware, cmd, binary):
        try:
            w32scu.StartService(serviceName=self.name)
        except WinT.error, e:
            if e.args[0] == werr.ERROR_ACCESS_DENIED:
                if not su_aware:
                    raise DaemonPrivilegeException(
                        'Starting Windows daemon service failed: '
                        'Administrator privileges are required!',
                        'ERROR_ACCESS_DENIED',
                        e.args[0]
                    )
                else:
                    self.__elevate(
                        binary=binary,
                        cmd=cmd,
                        timeout=self.setup_timeout
                    )
        finally:
            self.start(name=self.name)

    @classmethod
    def __elevate(cls, binary, cmd, timeout):
        hProc = w32sh_sh.ShellExecuteEx(
            nShow=w32con.SW_HIDE,
            fMask=(
                w32shcon.SEE_MASK_NOCLOSEPROCESS |
                w32shcon.SEE_MASK_FLAG_DDEWAIT
            ),
            lpVerb='runas',
            lpFile=binary,
            lpParameters=cmd
        )['hProcess']

        evCode = w32ev.WaitForSingleObject(hProc, timeout)
        if evCode == w32ev.WAIT_TIMEOUT:
            raise DaemonTimeoutError(
                    'Timeout expired while awaiting elevation operation to '
                    'complete!',
                    'timeout',
                    timeout,
                    'event',
                    evCode
            )
        elif evCode != w32ev.WAIT_OBJECT_0:
            raise DaemonError(
                'Unidentified event code during elevation request!',
                'event',
                evCode
            )

        procCode = w32ps.GetExitCodeProcess(hProc)
        if procCode != 0:
            raise DaemonPrivilegeException(
                'Elevation operation failed with process code: ',
                'process_code',
                procCode
            )

    @classmethod
    def start(cls, name, timeout=1, retries=30):
        svc_codes = w32scu.QueryServiceStatus(
            serviceName=name
        )
        while svc_codes[1] != w32svc.SERVICE_RUNNING:
            time.sleep(timeout)
            if retries < 0:
                raise DaemonTimeoutError(
                    'Querying for service status has failed!',
                    'timeout',
                    timeout,
                    'retries',
                    retries
                )
            retries = retries - 1
            svc_codes = w32scu.QueryServiceStatus(
                serviceName=name
            )

    def send(self, msg, timeout=0):
        # It is important to encode the message in ASCII otherwise it won't be
        # visible in the Event viewer log.
        # TODO: Some py2k vs py3k compatibility maybe???
        return self.pipe.write(
            payload=msg.encode('ascii', 'ignore'), timeout=timeout
        )

    def receive(self, timeout=0):
        return self.pipe.read(timeout=timeout)

    def close(self):
        self.pipe.close()
