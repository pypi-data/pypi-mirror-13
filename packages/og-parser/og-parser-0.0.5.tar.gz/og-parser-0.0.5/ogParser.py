from bs4 import BeautifulSoup

import urllib2
import re

class OpenGraphParser():
    def og_parser(selt, url):
        res = urllib2.urlopen(url).read()

        soup = BeautifulSoup(res, 'html.parser')
        print soup.title.string

        ogReg = re.compile('^og:')

        a = dict()

        for meta in soup.find_all('meta'):
            if bool(re.search(ogReg, str(meta.get('property')))):
                a[re.sub(ogReg, '', meta.get('property'))] =  meta.get('content') 
                print re.sub(ogReg, '', meta.get('property')), meta.get('content')

        return a
