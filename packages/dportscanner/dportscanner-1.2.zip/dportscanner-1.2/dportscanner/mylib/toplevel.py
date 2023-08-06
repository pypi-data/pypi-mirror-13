__author__ = 'David Dexter'
from dtld.dtld import TopLevelDomain as tld
def get_tld(url):
    top = tld(url)
    topld = top.get_top_level_domain()
    return topld