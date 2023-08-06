import bmt_tools as bmt

def WikiSearch():
    correct = 'no'
    while correct == 'no':
        searchTerm = input("What would you like to search?")
        url = _getWikiURL(searchTerm)

        WikiSoup = bmt.soupifyURL(url)

        results = _getWikiResults(WikiSoup)

        correct = _getCorrectResult(searchTerm,results)

    return results[int(correct)].find('a')['href']


def _getWikiURL(searchTerm):
    return 'http://en.wikipedia.org/w/index.php?title=Special%3ASearch&search=' + \
          searchTerm.replace(' ','+') + '&fulltext=Search'

def _getWikiResults(WikiSoup):
    return WikiSoup.find_all('div','mw-search-result-heading')

def _getCorrectResult(searchTerm,results):
    resultOptions = _printWikiResults(results)
    correct = input("title = " + searchTerm + "; Are any of these correct? (number or \"no\")")
    if correct not in [str(a) for a in resultOptions]+["no"]:
        correct = "no"
    return correct

def _printWikiResults(results):
    resultOptions = range(min([10,len(results)]))
    for i in resultOptions:
        print(str(i)+': '+results[i].text)
    return resultOptions

print(WikiSearch())