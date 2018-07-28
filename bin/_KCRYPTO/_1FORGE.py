import time  			#TO MEASURE EXECUTION TIMES,
import urllib2          #FOR CONNECTING TO NANOPOOL, WHICH HAS A MORE SOPHISTICATED API
import json             #FOR JSON OPERATIONS



def _getForex(apiKey, currencyPair):
    #BUILD URL, ISSUE API CALL, PARSE RESULTS INTO JSON
    url = "https://forex.1forge.com/1.0.3/quotes?api_key=" + apiKey + "&pairs=" + currencyPair

    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req)
    content = page.read()
    resultsList = json.loads(content)
    resultsD = resultsList[0]
    forexRate = resultsD['price']
    return forexRate
