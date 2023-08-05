# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the misc module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import generators
# Python native libraries.
import os
import sys


class Environment(object):

    """A class that contains useful utility methods."""

    @staticmethod
    def getSourceFilePath(name, extensionless=False):

        try:
            src_file = sys.modules[
                name
            ].__file__
        except AttributeError:
            # Executable modules have no __file__ attribute defined.
            src_file = sys.executable

        if extensionless:
            return os.path.splitext(
                os.path.abspath(src_file)
            )[0]
        else:
            return src_file

    @staticmethod
    def getSourceFileDir(name):
        return os.sep.join(
            Environment.getSourceFilePath(name).split(os.sep)[:-1]
        )

    @staticmethod
    def getPyVirtualEnv(folder, name):
        venv = os.path.expanduser('~') + os.sep + folder + os.sep + name
        py_bin = 'python'
        if sys.platform.startswith('win'):
            py_bin += '.exe'
        return venv + os.sep + 'Scripts' + os.sep + py_bin
