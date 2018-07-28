########################################
# VERSION:  1.0
# UPDATED:  3/1/2018
# DESCRIP:  crypto market delta loop operations
# NOTES:
########################################
import time  			#TO MEASURE EXECUTION TIMES,
from time import gmtime, strftime #AND TIMESTAMP API WRITES

#import sys
#sys.path.append('/_LOCALDATA/_PROGDATA/SCRIPTS/_CONFIG')
#import _CRYPTOCONFIG
import _OUTPUT
import _BINANCE
import _BTCMARKETS
import _GOOGLE


#---------------------------------------------------------------------------------------------------------------------------------------------------
def _main():
    scriptStartTime = time.time()

    _btcmTickerOps()
    _binanceTickerOps()
    _marketDeltaOps()

    scriptRunTime = {"ScriptRunTime_MARKEYLOOPVIZ.py":  time.time() - scriptStartTime}
    _OUTPUT._spitJSONoutToSplunk(scriptRunTime)
    _timestampGsheet()


def _btcmTickerOps():
    # DESCR:    Stripped down version of the BTCMARKETS version, just to update gSheet [InterMarketLoop] tab at the same time as this script now runs (every 1min rather than waiting on 5min timer for other update)
    # ARGS:     none
    # UPDATES:  gSheet ([InterMarketLoop] tab ONLY
    # RETURNS:  nothing
    #
    #COINS TO AUD
    btcmTkDict = {"kCryptoDictType": 'BTCMticker'}
    ######COIN CANT BE EXCHANGED ON BINANCE TO BITCOIN:   btcmTkDict.update(    {"BTC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("BTC", "AUD")} )
    btcmTkDict.update(    {"ETH-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("ETH", "AUD")} )
    btcmTkDict.update(    {"LTC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("LTC", "AUD")} )
    btcmTkDict.update(    {"ETC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("ETC", "AUD")} )
    ######COIN CANT BE EXCHANGED ON BINANCE TO BITCOIN:   btcmTkDict.update(    {"BCH-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("BCH", "AUD")} )
    btcmTkDict.update(    {"XRP-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("XRP", "AUD")} )
    #UPDATE GSHEETS WITH ABOVE
    btcmTickList_AUD    = [ [ "N/A", btcmTkDict['ETH-DATA']['lastPrice'], btcmTkDict['LTC-DATA']['lastPrice'], btcmTkDict['ETC-DATA']['lastPrice'], "N/A", btcmTkDict['XRP-DATA']['lastPrice'], ], ]
    _GOOGLE._publishToGoogleSheet(btcmTickList_AUD, 'USER_ENTERED', '[InterMarketLoop]!C8',       'COLUMNS')
    return

def _binanceTickerOps():
    # DESCR:    get tickers (xCoin-To-Bitcoin-Rate) for binance mainstream coins, spit them to splunk, update gsheet
    # ARGS:     none
    # UPDATES:  gSheet ([InterMarketLoop] tab ONLY
    # RETURNS:  nothing
    #
    BINcoinList         = ["ETH", "LTC", "ETC", "XRP"]              #NOTE THERE IS NO BITCOIN (AS WE ARE COMPARING TO BITCOIN!)
    BINdict = _BINANCE._BINapiNoAuth_getTickr("GET", "/api/v1/ticker/allPrices", BINcoinList)
    _OUTPUT._spitJSONoutToSplunk(BINdict)
    BINxCoinToBitcoinRatelist = [ [ "N/A", BINdict['ETH-BTC']['lastPrice'], BINdict['LTC-BTC']['lastPrice'], BINdict['ETC-BTC']['lastPrice'], "N/A", BINdict['XRP-BTC']['lastPrice'], ], ]
    _GOOGLE._publishToGoogleSheet(BINxCoinToBitcoinRatelist,'USER_ENTERED','[InterMarketLoop]!G8',   'COLUMNS')
    return


def _marketDeltaOps():
    # DESCR:    read market delta % from gSheet, pass to parse fucntion (alerting done there), spit parsed delta to splunk
    # ARGS:     none
    # UPDATES:  splunk
    # RETURNS:  nothing
    #
    googleSheetBlock    = _GOOGLE._readFromGoogleSheet('[InterMarketLoop]!P1:R13')
    deltaDictParsed     = _exchLoopDeltaParseLogic(googleSheetBlock)
    _OUTPUT._spitJSONoutToSplunk(deltaDictParsed)
    return


def _exchLoopDeltaParseLogic(googleSheetRangeBlock):
    # DESCR:    parse unclean gSheet data by walking it, row by row, extract market delta % values into clean list, conditionally alerting as we go,
    # UPDATES:  slack (alert)
    # RETURNS:  clean dictionary of exchange delta percentages:
    #   {
    #        "EXCHDELTA-BTCM-BINANCE": {
    #            "ETC": 0.0,
    #            "ETH": 3.008,
    #            "LTC": 3.596,
    #            "XRP": 2.29,
    #            "kCryptoDictType": "exchDelta",
    #            "myExDeltaFuncTime": 3.2901763916015625e-05,
    #            "slackThresh": 6.0
    #        },
    #        "kCryptoDictType": "exchDelta"
    #    }
    myExDeltaStartTime = time.time()
    slackWebhook = "https://hooks.slack.com/services/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"
    deltaDictParsed = {}
    deltaDictParsed = {"kCryptoDictType": 'exchDelta'}

    if not googleSheetRangeBlock:
        print('No data found.')
    else:
        #CHECK FOR BREACHES, FIRE ALERT IF ONE FOUND
        resetAlertValue = [ [ 'onAlert', ], ]
        currentRow = 1
        for row in googleSheetRangeBlock:
            #GET THE USER DEFINED ALERT THRESHOLD WHICH IS THE FIRST ROW, FIRST COLUMN OF THE DATA SET, AND ALSO THE MUTEFLAG (SECOND ROW, FIRST COLUMN)
            if (currentRow) == 1:
                triggerPercent = float(row[0])
            if (currentRow) == 2:
                muteFlag = row[0]

            #CODE TO HANDLE THE FACT THAT SOME VALUES IN row[0] ARE STRINGS, TRY TO CONVERT EVERYTHING TO FLOAT, AND WHEN IT FAILS, DONT THROW AN ERROR.... RESUTSET LOOKS LIKE: {"EXCHDELTA-BTCM-BINANCE": {".": "%", "BCH": "N/A", "BTC": "N/A", "ETC": "0.0006",............} }
            try:
                myFloat = float(row[0])
                deltaDictParsed.update({row[2]: myFloat*100})
            except ValueError:
                pass
            if ( myFloat > triggerPercent )  and  ( muteFlag != "y" ) :
                slackMessage = '*[%s%%]* delta on *[%s]* @%s' % (format(myFloat*100, '.1f') , row[2],  strftime("%H:%M"))
                _OUTPUT._pushMessageToSlack(slackWebhook, slackMessage)
            currentRow = currentRow + 1

    deltaDictParsed.update( {"myExDeltaFuncTime":  time.time() - myExDeltaStartTime} )
    #BUILD THE OUTER LAYER JSON WRAPPER
    exchDeltaDict = {"kCryptoDictType": 'exchDelta'}
    exchDeltaDict.update(    {"EXCHDELTA-BTCM-BINANCE":  deltaDictParsed})
    return exchDeltaDict

def _timestampGsheet():
    timeList            = [ [ strftime("%d/%m/%Y %H:%M:%S"), ], ]
    _GOOGLE._publishToGoogleSheet(timeList,         'USER_ENTERED', '[InterMarketLoop]!C20',          'COLUMNS')
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
