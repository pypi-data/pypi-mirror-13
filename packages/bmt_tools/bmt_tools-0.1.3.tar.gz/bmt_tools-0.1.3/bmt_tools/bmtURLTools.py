def soupifyURL(url):
    from bs4 import BeautifulSoup as BS
    
    request = requestURL(url)
    return BS(request.text)

def requestURL(url):
    from requests import get
    return get(url)

def jsonURL(url):
    request = requestURL(url)
    return request.json()

