from __future__ import absolute_import,unicode_literals

import socket
import tempfile

import synapse.dyndeps as s_dyndeps
import synapse.lib.socket as s_socket

from synapse.common import *
from synapse.links.common import *

serial = s_dyndeps.getDynMod('serial')

class SerialRelay(LinkRelay):
    '''
    Implements serial I/O based synapse LinkRelay.
    '''
    proto = 'serial'

    def _reqValidLink(self):
        if serial == None:
            raise NoSuchMod('serial')

    #def _getTempPath(self):
        #host = self.link[1].get('host')
        # use the host part to generate a local path
        #tdir = tempfile.gettempdir()
        #return os.path.join(tdir,host)

    #def _listen(self):
        #s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #s.bind( self._getTempPath() )
        #s.listen(120)

        #return s_socket.Socket(s, listen=True)
        
    #def _connect(self):
        #path = self._getTempPath()
        #s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        #s.connect(path)
        #return s_socket.Socket(s)

