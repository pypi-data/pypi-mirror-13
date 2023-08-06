# DTLD
Custom Top Level domain extractor

This is an example of a top level domain : wxyz.com or qbcd.net

How it works
DTLD extracts the root domain. It works by extracting from http|https|www protocol URLS

Example Code:

 from dtld.dtld import TopLevelDomain as tld

 url = 'http://github.com'

 App = tld.TopLevelDomain(url)

 domain = App.get_top_level_domain()

 print(domain)

 >>github.com

How to install

UNIX

    pip install dtld1.0

WINDOWS
    PYTHON 2
        py -m pip install dtld1.0

    PYTHON 3
        py -m pip install dtld1.0




