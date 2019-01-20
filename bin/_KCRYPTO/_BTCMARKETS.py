###################################################################################################### BTCMARKETS
#BTCMARKETS API
# KNOTES: authenticated API is complex....
#   https://github.com/limx0/btcmarkets is a total weapon and got me over the line!
#   https://github.com/BTCMarkets/api-client-python   <<<< ohh, and thia!
import hashlib          #FOR HMAC SHA256 SIGNING INTO BTCMARKETS
import hmac             #FOR HMAC SHA256 SIGNING INTO BTCMARKETS
import base64           #FOR HMAC SHA256 SIGNING INTO BTCMARKETS
import collections      #FOR HMAC SHA256 SIGNING INTO BTCMARKETS
#BTCM GLOBAL VARIABLES
BTCMapiBaseURL      = "https://api.btcmarkets.net/"


###################################################################################################### K HEADER CODE STARTS HERE:
import sys 				#for sys.stdout.write(plusCurlList)
import datetime  		#to convert epoch to human readable
import time  			#TO MEASURE EXECUTION TIMES,
from time import gmtime, strftime #AND TIMESTAMP API WRITES
import socket			#FOR DNS OPERATIONS
from subprocess import Popen, PIPE
import json             #FOR JSON OPERATIONS
import urllib           #FOR HTTP API
import urllib2          #FOR CONNECTING TO NANOPOOL, WHICH HAS A MORE SOPHISTICATED API
import requests         #FOR SLACK API POST.... note, this requires:   'pip install --upgrade requests'  (dont forget to then manually copy stuff from /Library/Python/2.7/site-packages --->  /Applications/Splunk/lib/python2.7/site-packages
import numbers
###################################################################################################### K HEADER

import _OUTPUT
import _GOOGLE


#---------------------------------------------------------------------------------------------------------------------------------------------------
# BTCMARKET FUNCTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------

def _BTCMbuildHeader(method, path, pubKey, priKey, postData=None):
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


def _BTCMapiAuth_getBal(method, path, pubKey, priKey):
    myBTCMStartTime = time.time()

    #BUILD URL, (authenticated) HEADER, AND ISSUE API CALL, PARSE RESULTS INTO JSON
    url = BTCMapiBaseURL + path
    hdr = _BTCMbuildHeader(method, path, pubKey, priKey)
    response = requests.get(url, headers=hdr)       #RESULTING JSON= SEE FOOTER OF THIS FILE
    data = json.loads(response.text)
    #print (data)
    resultsDict = {"zzBTCMjsonDlTime":  time.time() - myBTCMStartTime}
    resultsDict.update( {"kCryptoDictType": 'BTCMbalance'} )
    #FOR EACH COIN, BUILD A DICTIONARY LIKE BELOW, THAT SITS IN A LARGER DICTIONARY... RETURN THAT DICTIONARY
    #{
    #    "BCH": {
    #        "balance": 0.0
    #        "aaCoin": 'BCH'
    #    },
    #    "BTC": {
    #        "balance": 0.61699334
    #        "aaCoin": 'BTC'
    #    },
    #
    data3 = (filter(lambda data2: data2['currency'] == 'BTC', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )
    data3 = (filter(lambda data2: data2['currency'] == 'ETH', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )
    data3 = (filter(lambda data2: data2['currency'] == 'LTC', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )
    data3 = (filter(lambda data2: data2['currency'] == 'ETC', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )
    data3 = (filter(lambda data2: data2['currency'] == 'BCHABC', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )
    data3 = (filter(lambda data2: data2['currency'] == 'XRP', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )
    data3 = (filter(lambda data2: data2['currency'] == 'AUD', data))
    resultsDict.update(   {str(data3[0]['currency'])+'-BAL': {"balance": float(data3[0]['balance'] - data3[0]['pendingFunds'])/100000000, "aaCoin": data3[0]['currency'], "pending": float(data3[0]['pendingFunds'])/100000000, } } )

    #print (json.dumps(resultsDict, indent=4, sort_keys=True))
    return resultsDict


def _BTCMapiNoAuth_getTickr(coin, against):
    myBTCMStartTime = time.time()

    ## BTCmarkets API doco is here:  https://github.com/BTCMarkets/API    ( and more specifically https://github.com/BTCMarkets/API/wiki/Market-data-API )
    # NOTE this is a readonly public API hence no auth required (unlike account related operations)
    url = BTCMapiBaseURL + "market/" + coin + "/" + against + "/tick"
    response = urllib.urlopen(url)                  # RESULTING JSON = SEE FOOTER OF THIS FILE
    data = json.loads(response.read())

    resultsDict = {"zzBTCMjsonDlTime":  time.time() - myBTCMStartTime}
    resultsDict.update({"aaCoin":    data['instrument']})
    resultsDict.update({"bestAsk":   data['bestAsk']})
    resultsDict.update({"bestBid":   data['bestBid']})
    resultsDict.update({"lastPrice": data['lastPrice']})
    resultsDict.update({"timestamp": data['timestamp']})
    resultsDict.update({"volume24h": data['volume24h']})
    return resultsDict

def _resetAlert_btcmTicker(googleSheetRangeBlock):
    #ALERTS SHOULD BE RESET IF (FOR A LOW ALERT) THE PRICE *RAISES* ABOVE THE LOW ALERT VALUE AGAIN.  VICE VERSA FOR HIGH ALERT.
    #KNOTE THAT googleSheetRangeBlock WILL THOW OUT OF BOUNDS ERROR (i.e. when referencing row[5] IF YOU DONT HAVE DATA IN *ALL* CELLS IN THE GSHEET. ANNOYING !
    if not googleSheetRangeBlock:
        print('No data found.')
    else:
        #CHECK FOR BREACHES, FIRE ALERT IF ONE FOUND
        resetAlertValue = [ [ 'onAlert', ], ]
        currentRow = 8   #THIS NEEDS TO BE SET TO THE ROW NUMBER WHERE YOUR FIRST ROW IS
        for row in googleSheetRangeBlock:
            #LOGIC CAN BE TRICKY HERE>.. TIPS = MAKE SURE GSHEETS FORMATTING IS SIMPLE, NO COMMAS IE 1,001.00 IS BAD (CANT CONVERT TO FLOAT)... ALSO WITHOUT THE FLOAT CONVERSION THE BELOW MISBEHAVES...
            #print('%s, %s, %s, %s, %s, %s' % ( row[0], row[1], row[2], row[3], row[4], row[5] ))
            if (row[4] == "FIRED") and (float(row[1]) > float(row[2])) :
                _GOOGLE._publishToGoogleSheet(resetAlertValue, 'USER_ENTERED', '[CryptoSum]!F' + str(currentRow), 'COLUMNS')
            elif (row[5] == "FIRED") and (float(row[1]) < float(row[3])) :
                _GOOGLE._publishToGoogleSheet(resetAlertValue, 'USER_ENTERED', '[CryptoSum]!G' + str(currentRow), 'COLUMNS')
            currentRow = currentRow + 1
    return

def _breachCheck_btcmTicker(googleSheetRangeBlock):
    slackWebhook = 'https://hooks.slack.com/services/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'
    if not googleSheetRangeBlock:
        print('No data found.')
    else:
        #CHECK FOR BREACHES, FIRE ALERT IF ONE FOUND
        resetAlertValue = [ [ 'FIRED', ], ]
        currentRow = 8   #THIS NEEDS TO BE SET TO THE ROW NUMBER WHERE YOUR FIRST ROW IS
        for row in googleSheetRangeBlock:
            #LOGIC CAN BE TRICKY HERE>.. TIPS = MAKE SURE GSHEETS FORMATTING IS SIMPLE, NO COMMAS IE 1,001.00 IS BAD (CANT CONVERT TO FLOAT)... ALSO WITHOUT THE FLOAT CONVERSION THE BELOW MISBEHAVES...
            #print('%s, %s, %s, %s, %s, %s' % ( row[0], row[1], row[2], row[3], row[4], row[5] ))
            if (float(row[1]) < float(row[2]))  and  (row[4] != "FIRED") :
                #print('%s LOW BREECH!' % (row[0]))
                slackMessage = '[*%s @ $%s*] _LOW_ breach! _(threshold was $%s)_ :point_down:'  % (row[0], row[1], row[2])
                _OUTPUT._pushMessageToSlack(slackWebhook, slackMessage)
                _GOOGLE._publishToGoogleSheet(resetAlertValue, 'USER_ENTERED', '[CryptoSum]!F' + str(currentRow), 'COLUMNS')
            elif (float(row[1]) > float(row[3]))  and  (row[5] != "FIRED") :
                #print('%s HIGH BREECH!' % (row[0]))
                slackMessage = '[*%s @ $%s*] _HIGH_ breach! _(threshold was $%s)_ :point_up:'  % (row[0], row[1], row[3])
                _OUTPUT._pushMessageToSlack(slackWebhook, slackMessage)
                _GOOGLE._publishToGoogleSheet(resetAlertValue, 'USER_ENTERED', '[CryptoSum]!G' + str(currentRow), 'COLUMNS')
            currentRow = currentRow + 1
    return
