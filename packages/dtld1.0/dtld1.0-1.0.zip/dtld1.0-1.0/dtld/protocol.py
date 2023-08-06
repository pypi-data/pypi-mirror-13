__author__ = 'David Dexter'
import re
class Protocol:
    def __init__(self, userinput):
        self.input = userinput

    def check_protocol(self):
        prot = 'http|https|www'
        Obj = re.compile(prot, flags=re.IGNORECASE)
        srchObj = Obj.findall(self.input)
        if srchObj == []:
            return False
        else:
            return True




