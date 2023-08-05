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


class DaemonPrivilegeException(Exception):

    """A class for raising daemon privilege errors."""

    """
        This class efficiently communicates to the user when a daemon privilege
        escalation (usually to admin (Windows) or sudo (Linux) ) is required.
    """

    def __init__(self, message, attribute_key, attribute_value, *args):
        """Default initialization class method."""
        """
            Sets the required parameters when throwing a daemon privilege
            exception.
            Apart from the exception message (string), parameters are pairs of
            (attribute key, attribute value) aka pairs of (string, object)
            values.
        """
        self.message = message
        self.attribute_key = attribute_key
        self.attribute_value = attribute_value
        self.arglist = []
        for arg in args:
            self.arglist.append(arg)
        super(DaemonPrivilegeException, self).__init__(
            message, attribute_key, attribute_value, *args
        )
