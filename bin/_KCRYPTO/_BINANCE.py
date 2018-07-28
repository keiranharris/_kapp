import time  			#TO MEASURE EXECUTION TIMES,
import hashlib          #FOR HMAC SHA256 SIGNING INTO
import hmac             #FOR HMAC SHA256 SIGNING INTO
import base64
import collections      #FOR HMAC SHA256 SIGNING INTO BTCMARKETS
import requests
import json             #FOR JSON OPERATIONS

BINapiBaseURL      = "https://www.binance.com"

###################################################################################################### BINANCE
#K-BINANCE-API-KEY-LABEL
# CREATE API KEY: https://www.binance.com/userCenter/createApi.html
# DOCO: https://www.binance.com/restapipub.html
# GIT HIB COMMUNITY PYTHON CODE:   https://github.com/binance-exchange/python-binance   (and doco https://python-binance.readthedocs.io/en/latest/)

###################################################################################################### BINANCE


#---------------------------------------------------------------------------------------------------------------------------------------------------
# BINANCE FUNCTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------
def _BINbuildHeader(method, path, pubKey, priKey, postData=None):
    timestamp = str(int(time.time() * 1000))
    string_body = path + "\n" + timestamp + "\n"
    if postData is not None:
        string_body += post_data

    b64_secret = base64.standard_b64decode(priKey)
    rsig = hmac.new(b64_secret, string_body.encode("utf-8"), hashlib.sha512)
    bsig = base64.standard_b64encode(rsig.digest()).decode("utf-8")
    return collections.OrderedDict([
        ("Accept", "application/json"),
        ("Accept-Charset", "UTF-8"),
        ("Content-Type", "application/json"),
        ("apikey", pubKey.decode("utf-8")),
        ("timestamp", timestamp),
        ("signature", bsig),
    ])


def _BINapiNoAuth_getTickr(method, path, coinList):
    myBINStartTime = time.time()
    #BUILD URL, ISSUE API CALL, PARSE RESULTS INTO JSON
    url = BINapiBaseURL + path

    hdr = _BINbuildHeader(method, path, "blah", "blah")
    response = requests.get(url, headers=hdr)           # RESULTING JSON = SEE FOOTER OF THIS FILE

    data = json.loads(response.text)
    #print (data)

    resultsDict = {"zzBINTjsonDlTime":  time.time() - myBINStartTime}
    resultsDict.update({"kCryptoDictType": 'BINticker'})

    for i in range(len(coinList)):
#        if coinList[i] == "BTC":
#            continue
        #THIS CODE AUTOMATES THE CREATION OF THE FOLLOWING, PER COIN:
        #    data3 = (filter(lambda data2: data2['symbol'] == 'ETHBTC', data))
        #    resultsDict.update({    "ETH-BTC": {"lastPrice": data3[0]['price'], "aaCoin": 'ETH', } } )
        coinBTC = coinList[i] + "BTC"
        #LAMBDA WORKS LIKE:  return = (filterOnCONDITION(lambda ARG-REMAP: CONDITION, ARGUMENT))
        data3 = (filter(lambda lamDict: lamDict['symbol'] == coinBTC, data))
        resultsDict.update({   coinList[i] + "-BTC":   {"lastPrice": data3[0]['price'], "aaCoin": coinList[i], } } )

    return resultsDict


def _BINapiAuth_getAccount(method, path, pubKey, priKey, coinList, postData=None):
    myBINAcStartTime = time.time()
    mytimestamp = format(myBINAcStartTime * 1000, '.0f')    #FORMAT REMOVES SCIENTIFIC NOTATION, ZERO DECIMAL PLACES. API EXPECTS THIS.
    string_body = "timestamp=" + str(mytimestamp)
    sig = hmac.new(priKey, string_body.encode("utf-8"), hashlib.sha256)
    #CAN INTERACT WITH API BY A QUERYSTRING (OTHER METHODS AVAILABLE SEE LINK TO DOCS IN NOTES ABOVE)
    url = BINapiBaseURL + path + "?" + string_body + "&signature=" + sig.hexdigest()
    hdr = collections.OrderedDict([
        ("Accept", "application/json"),
        ("Accept-Charset", "UTF-8"),
        ("Content-Type", "application/json"),
        ("X-MBX-APIKEY", pubKey.decode("utf-8")),
    ])
#    print(url)
#    print(hdr)
    response = requests.get(url, headers=hdr)       #RESULTING JSON= SEE FOOTER OF THIS FILE
    data = json.loads(response.text)
    #NOTE - THERE CAN BE A NTP PROBLEM - EVIDENT BY PRINTING "data" IE:   {u'msg': u"Timestamp for this request was 1000ms ahead of the server's time.", u'code': -1021}
    print (data)

    #EXTRACT JUST THE BALANCES (which in itself a list of dictionaries) PART OF THE DICTIONARY OUT TO A NEW LIST. THIS IS CAUSE I HAD PROBLEMS WITH LAMBDA BELOW DIVING INTO A SECOND LEVEL OF A DICTIONARY
    balOnlyDict = data['balances']
    print(balOnlyDict)
    resultsDict = {"zzBINACjsonDlTime":  time.time() - myBINAcStartTime}
    resultsDict.update({"kCryptoDictType": 'BINAccount'})

    for i in range(len(coinList)):
        #LAMBDA WORKS LIKE:  return = (filterOnCONDITION(lambda ARG-REMAP: CONDITION, ARGUMENT))
        selectedDict = (filter(lambda lamDict: lamDict['asset'] == coinList[i], balOnlyDict))
        resultsDict.update({  coinList[i]:  {"balance": selectedDict[0]['free'], "pending": selectedDict[0]['locked'], "aaCoin": selectedDict[0]['asset'], } } )

    return resultsDict


def _makeBINaltCoinsOfInterestList(googleSheetBlock):
    myBINaltCoinStartTime = time.time()
    altCoinList = []
    for row in googleSheetBlock:
        #ONLY APPEND TO LIST IF THERES DATA IN CELL
        if row[0] != "":
            altCoinList.append(row[0])
    return altCoinList
