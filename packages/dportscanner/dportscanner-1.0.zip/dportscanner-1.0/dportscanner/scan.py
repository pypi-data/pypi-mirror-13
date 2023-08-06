__author__ = 'David Dexter'
from dportscanner.mylib.address import GetAddress
from dportscanner.mylib.toplevel import get_tld as gtld
from dportscanner.mylib.mapper import Nmap
class PortScanner:
    def __init__(self,url):
        self.url = url
    def scan(self):
        ###get the top level domain
        top_domain = gtld(self.url)

        ###get the ipv4
        addr = GetAddress(top_domain)
        ipaddr = addr.get_address()
        if ipaddr == False:
            print('Please check your Intenet Connection')
        else:
            scan = Nmap(ipaddr)
            rep = scan.ipmapper()
            return rep













