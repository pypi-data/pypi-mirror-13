# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Python script to request service privileged operations via UAC/gksudo."""

#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
# Python native libraries.
import sys
import argparse

# Python 3rd party libraries.
if sys.platform.startswith('win'):
    import win32serviceutil as w32scu
    import win32service as w32svc


def __install(args):
    if sys.platform.startswith('win'):
        if args.mode is None or args.mode == 'delayed':
            delayed_start = True
        else:
            delayed_start = False
        w32scu.InstallService(
            pythonClassString=args.py_class,
            serviceName=args.name,
            displayName=args.display_name,
            description=args.description,
            startType=w32svc.SERVICE_AUTO_START,
            delayedstart=delayed_start
        )


def __delete(args):
    if sys.platform.startswith('win'):
        w32scu.RemoveService(
            serviceName=args.name
        )


def __activate(args):
    if sys.platform.startswith('win'):
        w32scu.StartService(
            serviceName=args.name
        )


def __stop(args):
    if sys.platform.startswith('win'):
        w32scu.StopService(
            serviceName=args.name
        )

if __name__ == "__main__":

    cli = argparse.ArgumentParser(
        prog='Administrator.py',
        description='CRAPI CLI: Windows/Linux daemon service administrator.',
        epilog='CRAPI licensing is governed under the ASF 2.0 license terms.'
    )
    cli_sub = cli.add_subparsers()

    # Install.
    install = cli_sub.add_parser(
        'install', help='Install a Windows/Linux daemon service.'
    )
    install.add_argument(
        'name',
        action='store',
        help='Name of the Windows/Linux daemon service.'
    )
    install.add_argument(
        'display_name',
        action='store',
        help='Display name of the Windows/Linux daemon service.'
    )
    install.add_argument(
        'description',
        action='store',
        help='Description of the Windows/Linux daemon service.'
    )
    install.add_argument(
        'py_class',
        action='store',
        help='(Windows only) Python class entry point of the daemon service: '
             'must be of the form \'full//path//to//module.where.file.exists\''
    )
    install.add_argument(
        'mode',
        nargs='?',
        action='store',
        choices=('auto', 'delayed', '3', '5'),
        help='The daemon service startup time. In Windows the startup mode '
             'can be either automatic or delayed (default). In Linux, the '
             'init level can be either 3 or 5 (default).'
    )
    install.set_defaults(func=__install)

    # update = cli_sub.add_parser(
    #     'update', help='Update a Windows/Linux daemon service.'
    # )
    # Delete.
    delete = cli_sub.add_parser(
        'delete', help='Delete a Windows/Linux daemon service.'
    )
    delete.add_argument(
        'name',
        action='store',
        help='Name of the Windows/Linux daemon service.'
    )
    delete.set_defaults(func=__activate)

    # Activate (start).
    activate = cli_sub.add_parser(
        'activate', help='Start a Windows/Linux daemon service.'
    )
    activate.add_argument(
        'name',
        action='store',
        help='Name of the Windows/Linux daemon service.'
    )
    activate.set_defaults(func=__activate)
    # Stop (suspend).
    stop = cli_sub.add_parser(
        'stop', help='Stop a Windows/Linux daemon service.'
    )
    stop.add_argument(
        'name',
        action='store',
        help='Name of the Windows/Linux daemon service.'
    )
    stop.set_defaults(func=__stop)

    # prog_args.add_argument(
    #     '-u', '--update', nargs=5, dest='install',
    #     help='Update a Windows/Linux daemon service.'
    # )
    # mtnc_args.add_argument(
    #     '-p', '--pause', nargs=1, dest='pause',
    #     help='Pause a Windows/Linux daemon service.'
    # )

    usr_args = cli.parse_args()
    usr_args.func(usr_args)
