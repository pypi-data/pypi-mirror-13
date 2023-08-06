__author__ = 'David Dexter'
from dtld.protocol import  Protocol
from dtld.top_domain import TopDomain
from dtld.startfunc import String
class TopLevelDomain:
    def __init__(self,domain):
        self.domain = domain
    def get_top_level_domain(self):
        ##check for http/https://www
        string = String(self.domain)
        strVar = string.formatter()
        if strVar == False:
            check = Protocol(self.domain)
            checkDM = check.check_protocol()
            if checkDM == False:
                print('Invalid Domain')
            else:
                get = TopDomain(self.domain)
                srch = get.extractor()
                if srch == False:
                    print ('Could not get domain')
                else:
                    return srch
        else:
            return strVar







