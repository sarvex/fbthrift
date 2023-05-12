from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from .TSocket import TSocket
from .TTransport import TTransportException
import socket


class TSocketOverHttpTunnel(TSocket):
    def __init__(self, host, port, proxy_host, proxy_port):
        TSocket.__init__(self, proxy_host, proxy_port)
        try:
            # Use IP address since sometimes proxy_host cannot resolve
            # external hostnames using unbound
            self.remote_host = socket.gethostbyname(host)
        except socket.error as e:
            raise TTransportException(TTransportException.NOT_OPEN, str(e))
        self.remote_port = port

    def open(self):
        TSocket.open(self)
        self.write("CONNECT %s:%d HTTP/1.1\r\nHost: %s:%d\r\n\r\n" % (
            self.remote_host, self.remote_port,
            self.remote_host, self.remote_port))
        res = self.read(4096)
        try:
            status = res.split()[1]
            if status != '200':
                self.close()
                raise TTransportException(
                    TTransportException.NOT_OPEN,
                    f"Error response from proxy server: {res}",
                )
        except IndexError:
            self.close()
            raise TTransportException(
                TTransportException.NOT_OPEN,
                f"Error response from proxy server: {res}",
            )
