__author__ = 'David Dexter'
import socket
class GetAddress:
    def __init__(self,url):
        self.url = url
    def get_address(self):
        try:
           ipaddr = socket.gethostbyname(self.url)
           return ipaddr
        except socket.gaierror:
            return False








