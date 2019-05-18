
#---------------------------------------------------------------------------------------------------------------------------------------------------
# K-HEADERS
import sys
sys.path.append('/_LOCALDATA/_PROGDATA/SCRIPTS/_CONFIG')
import _CRYPTOCONFIG
import _OUTPUT
import _GOOGLE
import _BTCMARKETS
import _KRACKEN
#import _1FORGE   (moved off these guiys after 1forge started charging for their API - 20190516)
import _FOREX

import time  			#TO MEASURE EXECUTION TIMES,
from time import gmtime, strftime #AND TIMESTAMP API WRITES

def _main():
    scriptStartTime = time.time()

    _btcmTickerOps()
    _arbKrakenEUR()
    _arbKrakenGBP()
    _forexRates()
    _timestampGsheet()
    _readDeltaSpitToSplunk()

    scriptRunTime = {"ScriptRunTime_ARBVIZ.py":  time.time() - scriptStartTime}
    _OUTPUT._spitJSONoutToSplunk(scriptRunTime)


def _btcmTickerOps():
    #COINS TO AUD
    btcmTkDict = {"kCryptoDictType": 'BTCMticker'}
    btcmTkDict.update(    {"BTC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("BTC", "AUD")} )
    btcmTkDict.update(    {"ETH-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("ETH", "AUD")} )
    btcmTkDict.update(    {"LTC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("LTC", "AUD")} )
    btcmTkDict.update(    {"ETC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("ETC", "AUD")} )
    btcmTkDict.update(    {"BCHABC-DATA": _BTCMARKETS._BTCMapiNoAuth_getTickr("BCHABC", "AUD")} )
    btcmTkDict.update(    {"XRP-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("XRP", "AUD")} )

    #UPDATE GSHEETS WITH ABOVE
    btcmTickList_AUD    = [ [ btcmTkDict['BTC-DATA']['lastPrice'], btcmTkDict['ETH-DATA']['lastPrice'], btcmTkDict['LTC-DATA']['lastPrice'], btcmTkDict['ETC-DATA']['lastPrice'], btcmTkDict['BCHABC-DATA']['lastPrice'], btcmTkDict['XRP-DATA']['lastPrice'], ], ]
#    btcmTickList_AUD    = [ [ btcmTkDict['BTC-DATA']['lastPrice'], btcmTkDict['ETH-DATA']['lastPrice'], btcmTkDict['LTC-DATA']['lastPrice'], btcmTkDict['ETC-DATA']['lastPrice'], btcmTkDict['XRP-DATA']['lastPrice'], ], ]

    _GOOGLE._publishToGoogleSheet(btcmTickList_AUD, 'USER_ENTERED', '[arbFIAT]!C8',       'COLUMNS')
    return


def _arbKrakenEUR():
    coinsList = ['XBTEUR','ETHEUR','LTCEUR','ETCEUR','BCHEUR','XRPEUR']
    resultsDict = _KRACKEN._KRACKENapiNoAuth_getTickr(coinsList)
    #UPDATE GSHEETS WITH ABOVE
    resultsList    = [ [ resultsDict['XBTEUR']['lastPrice'], resultsDict['ETHEUR']['lastPrice'], resultsDict['LTCEUR']['lastPrice'], resultsDict['ETCEUR']['lastPrice'], resultsDict['BCHEUR']['lastPrice'], resultsDict['XRPEUR']['lastPrice'], ], ]
    _GOOGLE._publishToGoogleSheet(resultsList, 'USER_ENTERED', '[arbFIAT]!D8',       'COLUMNS')


def _arbKrakenGBP():
    coinsList = ['XBTGBP','ETHGBP']
    resultsDict = _KRACKEN._KRACKENapiNoAuth_getTickr(coinsList)
    #UPDATE GSHEETS WITH ABOVE
    resultsList    = [ [ resultsDict['XBTGBP']['lastPrice'], resultsDict['ETHGBP']['lastPrice'], ], ]
    _GOOGLE._publishToGoogleSheet(resultsList, 'USER_ENTERED', '[arbFIAT]!G8',       'COLUMNS')


def _forexRates():
    forexEURAUD = _FOREX._getForex('EUR', 'AUD')
    forexGBPAUD = _FOREX._getForex('GBP', 'AUD')
#    forexGBPAUD = _1FORGE._getForex(my1forgeAPIkey,'GBPAUD')
#    forexEURAUD = 1.666666
#    forexGBPAUD = 1.888888
    resultsList = [ [ forexEURAUD,forexGBPAUD, ], ]
    _GOOGLE._publishToGoogleSheet(resultsList, 'USER_ENTERED', '[arbFIAT]!C2',       'COLUMNS')


def _timestampGsheet():
    timeList            = [ [ strftime("%d/%m/%Y %H:%M:%S"), ], ]
    _GOOGLE._publishToGoogleSheet(timeList,         'USER_ENTERED', '[arbFIAT]!F2',          'COLUMNS')
    return

def _readDeltaSpitToSplunk():
    googleSheetBlock    = _GOOGLE._readFromGoogleSheet('[arbFIAT]!F8:F13')
    deltaDict = {"kCryptoDictType": 'exchArbDeltas'}
    #SLOPPY CODE HERE (TO DO WITH THE FACT THE googleSheetBlock IS A LIST OF LISTS THAT NEED TO BE POP'd).... COME BACK AND FIXUP (MAKE A LOOP, ITERATING COINLIST) WHEN I HAVE TIME.....
    innerList = googleSheetBlock[0]
    deltaDict.update ( {"BTC": {"remoteExchange": "kracken", "currencyBase" : "EUR", "delta": float(innerList[0])} } )
    innerList = googleSheetBlock[1]
    deltaDict.update ( {"ETH": {"remoteExchange": "kracken", "currencyBase" : "EUR", "delta": float(innerList[0])} } )
    innerList = googleSheetBlock[2]
    deltaDict.update ( {"LTC": {"remoteExchange": "kracken", "currencyBase" : "EUR", "delta": float(innerList[0])} } )
    innerList = googleSheetBlock[3]
    deltaDict.update ( {"ETC": {"remoteExchange": "kracken", "currencyBase" : "EUR", "delta": float(innerList[0])} } )
    innerList = googleSheetBlock[4]
    deltaDict.update ( {"BCHABC": {"remoteExchange": "kracken", "currencyBase" : "EUR", "delta": float(innerList[0])} } )
    innerList = googleSheetBlock[5]
    deltaDict.update ( {"XRP": {"remoteExchange": "kracken", "currencyBase" : "EUR", "delta": float(innerList[0])} } )
    _OUTPUT._spitJSONoutToSplunk(deltaDict)
    return

#---------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN CODE INVOKE POINT
#---------------------------------------------------------------------------------------------------------------------------------------------------
_main()

#---------------------------------------------------------------------------------------------------------------------------------------------------
# JSON DATA STRUCTURES
#---------------------------------------------------------------------------------------------------------------------------------------------------
'''
'''
