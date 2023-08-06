__author__ = 'David Dexter'
import nmap
class Nmap:
    def __init__(self, ipaddress):
        self.ipaddress = ipaddress

    def ipmapper(self):
        nm = nmap.PortScanner()
        nm.scan(self.ipaddress)
        status = 'IP STATUS : {state}'.format(state = nm[self.ipaddress].state())
        stslst = []
        stslst.append(status)
        protocols = nm[self.ipaddress].all_protocols()
        for protocol in protocols:
            protos = 'FOUND : {proto}'.format(proto = protocol)
            prtlst = []
            prtlst.append(protos)
            lport = nm[self.ipaddress][protocol].keys()
            portlst = []
            for port in lport:
                scnPort = '{port}'.format(port=port)
                scnStatus = '{status}'.format(status=nm[self.ipaddress][protocol][port]['state'])
                portStatus = {'PORT': scnPort, 'STATE': scnStatus}
                portlst.append(portStatus)
        report = {}
        report['status'] = stslst
        report['protocols'] = prtlst
        report['ports'] = portlst
        return report







