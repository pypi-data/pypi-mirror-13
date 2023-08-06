__author__ = 'David Dexter'
import re

class String:
    def __init__(self,url):
        self.url = url

    def formatter(self):
        pattern = 'http|https|www'
        srchObj = re.compile(pattern,flags=re.IGNORECASE)
        obj = srchObj.findall(self.url)
        if len(obj) == 2:
            spliPat = obj[1]+'.'
            topURL =  re.split(spliPat, self.url)
            topDM = topURL[1]
            return topDM
        else:
            return False




