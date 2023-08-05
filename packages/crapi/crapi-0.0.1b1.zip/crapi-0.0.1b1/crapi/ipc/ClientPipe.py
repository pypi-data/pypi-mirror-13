# Copyright (C) 2014/15 - Iraklis Diakos (hdiakos@outlook.com)
# Pilavidis Kriton (kriton_pilavidis@outlook.com)
# All Rights Reserved.
# You may use, distribute and modify this code under the
# terms of the ASF 2.0 license.
#

"""Part of the ipc module."""

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import crapi.ipc.Pipe as Pipe


class ClientPipe(Pipe.Pipe):

    def __init__(self, name='', ptype=Pipe.Pipe.Type.NAMED,
                 mode=Pipe.Pipe.Mode.DUPLEX, channel=Pipe.Pipe.Channel.MESSAGE,
                 transport=Pipe.Pipe.Transport.ASYNCHRONOUS, sa=None):

        super(ClientPipe, self).__init__(
            name=name, ptype=ptype, mode=mode, channel=channel,
            transport=transport, view=Pipe.Pipe.View.CLIENT, instances=0,
            buf_sz=[0, 0], sa=sa
        )
