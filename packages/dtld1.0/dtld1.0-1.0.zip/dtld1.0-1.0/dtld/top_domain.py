__author__ = 'David Dexter'
import re
class TopDomain:
    def __init__(self, domain):
        self.domain = domain
    def extractor(self):
        prot = r'http://|https://|www.'
        Obj = re.compile(prot, flags=re.IGNORECASE)
        search = Obj.search(self.domain)
        if search == None:
            return False
        else:
            dm = re.split(prot, self.domain)
            domain = dm[1]
            return domain


