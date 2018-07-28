########################################
# VERSION:  1.1
# UPDATED:  24/12/2017
# DESCRIP:  crypto GET operations
# NOTES:
########################################
import time  			#TO MEASURE EXECUTION TIMES,
from time import gmtime, strftime #AND TIMESTAMP API WRITES

import sys
sys.path.append('/_LOCALDATA/_PROGDATA/SCRIPTS/_CONFIG')
import _CRYPTOCONFIG

import _OUTPUT
import _BINANCE
import _BTCMARKETS
import _GOOGLE
import _NANOPOOL

BTCMapiKeyPub_m     = _CRYPTOCONFIG.BTCMapiKeyPub_m
BTCMapiKeyPri_m     = _CRYPTOCONFIG.BTCMapiKeyPri_m

BINapiKeyPub_m      = _CRYPTOCONFIG.BINapiKeyPub_m
BINapiKeyPri_m      = _CRYPTOCONFIG.BINapiKeyPri_m

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _main():
    scriptStartTime = time.time()

    _btcmTickerOps()
    _btcmAccountOps()
#    _binanceAccountOps()
    _portfolioOps()
    _thresholdOps()
    _NANOPOOL._nanoPoolOps()
    _timestampGsheet()

    #_OUTPUT_logToFile()
    scriptRunTime = {"ScriptRunTime_CRYPTOVIZ.py":  time.time() - scriptStartTime}
    _OUTPUT._spitJSONoutToSplunk(scriptRunTime)

def _btcmTickerOps():
    #COINS TO AUD
    btcmTkDict = {"kCryptoDictType": 'BTCMticker'}
    btcmTkDict.update(    {"BTC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("BTC", "AUD")} )
    btcmTkDict.update(    {"ETH-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("ETH", "AUD")} )
    btcmTkDict.update(    {"LTC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("LTC", "AUD")} )
    btcmTkDict.update(    {"ETC-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("ETC", "AUD")} )
    btcmTkDict.update(    {"BCH-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("BCH", "AUD")} )
    btcmTkDict.update(    {"XRP-DATA":    _BTCMARKETS._BTCMapiNoAuth_getTickr("XRP", "AUD")} )
    _OUTPUT._spitJSONoutToSplunk(btcmTkDict)
    #UPDATE GSHEETS WITH ABOVE
    btcmTickList_AUD    = [ [ btcmTkDict['BTC-DATA']['lastPrice'], btcmTkDict['ETH-DATA']['lastPrice'], btcmTkDict['LTC-DATA']['lastPrice'], btcmTkDict['ETC-DATA']['lastPrice'], btcmTkDict['BCH-DATA']['lastPrice'], btcmTkDict['XRP-DATA']['lastPrice'], ], ]
    _GOOGLE._publishToGoogleSheet(btcmTickList_AUD, 'USER_ENTERED', '[CryptoSum]!C8:C13',       'COLUMNS')

    return

def _btcmAccountOps():
    balancesDict = _BTCMARKETS._BTCMapiAuth_getBal("GET", "/account/balance", BTCMapiKeyPub_m, BTCMapiKeyPri_m)
    _OUTPUT._spitJSONoutToSplunk(balancesDict)
    BTCMBalList  = [ [ balancesDict['BTC-BAL']['balance'], balancesDict['ETH-BAL']['balance'], balancesDict['LTC-BAL']['balance'], balancesDict['ETC-BAL']['balance'], balancesDict['BCH-BAL']['balance'], balancesDict['XRP-BAL']['balance'], balancesDict['AUD-BAL']['balance'],  ], ]
    BTCMPendList = [ [ balancesDict['BTC-BAL']['pending'], balancesDict['ETH-BAL']['pending'], balancesDict['LTC-BAL']['pending'], balancesDict['ETC-BAL']['pending'], balancesDict['BCH-BAL']['pending'], balancesDict['XRP-BAL']['pending'], balancesDict['AUD-BAL']['pending'],  ], ]
    _GOOGLE._publishToGoogleSheet(BTCMBalList, 'USER_ENTERED','[CryptoSum]!I8',   'COLUMNS')
    _GOOGLE._publishToGoogleSheet(BTCMPendList,'USER_ENTERED','[CryptoSum]!J8',   'COLUMNS')
    return


def _binanceAccountOps():
    #GET MAINSTREAM COIN ACCOUNT/BALANCE DETAILS - MAINSTREAM COINS
    BINcoinList         = ["BTC", "ETH", "LTC", "ETC", "XRP"]
#    BINcoinList         = ["BTC"]
    BINacDict           = _BINANCE._BINapiAuth_getAccount("GET", "/api/v3/account", BINapiKeyPub_m, BINapiKeyPri_m, BINcoinList)

    _OUTPUT._spitJSONoutToSplunk(BINacDict)
    BINaclist           = [ [ BINacDict['BTC']['balance'], BINacDict['ETH']['balance'], BINacDict['LTC']['balance'], BINacDict['ETC']['balance'], "N/A", BINacDict['XRP']['balance'], ], ]
    BINpendlist         = [ [ BINacDict['BTC']['pending'], BINacDict['ETH']['pending'], BINacDict['LTC']['pending'], BINacDict['ETC']['pending'], "N/A", BINacDict['XRP']['pending'], ], ]
    _GOOGLE._publishToGoogleSheet(BINaclist,  'USER_ENTERED','[CryptoSum]!N8',   'COLUMNS')
    _GOOGLE._publishToGoogleSheet(BINpendlist,'USER_ENTERED','[CryptoSum]!O8',   'COLUMNS')

    #GET ALT-COIN ACCOUNT/BALANCE DETAILS (these vary, hence allow to be driven by user input on the gsheet)
    #GET LIST OF COINS FIRST
    googleSheetBlock    = _GOOGLE._readFromGoogleSheet('[CryptoSum]!S8:S21')
    myBINaltCoinList    = _BINANCE._makeBINaltCoinsOfInterestList(googleSheetBlock)

    #NEXT GET BALANCES OF THOSE COINS
    BINaltAcDict        = _BINANCE._BINapiAuth_getAccount("GET", "/api/v3/account", BINapiKeyPub_m, BINapiKeyPri_m, myBINaltCoinList)

    _OUTPUT._spitJSONoutToSplunk(BINaltAcDict)
    BINaltBalList = []
    BINaltPenList = []
    for i in range(len(myBINaltCoinList)):
        BINaltBalList.append(BINaltAcDict[myBINaltCoinList[i]]['balance'])
        BINaltPenList.append(BINaltAcDict[myBINaltCoinList[i]]['pending'])

    gSheetListOfListsBal = [ BINaltBalList, ]
    gSheetListOfListsPen = [ BINaltPenList, ]
    _GOOGLE._publishToGoogleSheet(gSheetListOfListsBal,'USER_ENTERED','[CryptoSum]!T8',   'COLUMNS')
    _GOOGLE._publishToGoogleSheet(gSheetListOfListsPen,'USER_ENTERED','[CryptoSum]!U8',   'COLUMNS')

    #GET VALUES OF THOSE COINS AGAINST BITCOIN (BINANCE DOES NOT DO AUD)
    BINaltDict = _BINANCE._BINapiNoAuth_getTickr("GET", "/api/v1/ticker/allPrices", myBINaltCoinList)
#    _OUTPUT._spitJSONoutToSplunk(BINaltDict)
    BINaltExRateList = []
    for i in range(len(myBINaltCoinList)):
        coinBTC = myBINaltCoinList[i] + "-BTC"
        BINaltExRateList.append(BINaltDict[coinBTC]['lastPrice'])

    gSheetListOfLists = [ BINaltExRateList, ]
    _GOOGLE._publishToGoogleSheet(gSheetListOfLists,'USER_ENTERED','[CryptoSum]!V8',   'COLUMNS')

    return

def _portfolioOps():
    # DESCR:    read in portfolio and summary values from gSheet (hardword has already been done there), so it can be spat to splunk for graphing
    # ARGS:     none
    # UPDATES:  splunk
    # RETURNS:  structure like below:
    #    {
    #        "KM-PORTFOLIO": {
    #            "AUDbtcmAUD": 20349.69,
    #            "BCHbinAUD": 0.0,
    #            "BCHbtcmAUD": 0.0,
    #            "BTCbinAUD": 843.83,
    #            "BTCbtcmAUD": 0.0,
    #            "ETCbinAUD": 0.1,
    #            "ETCbtcmAUD": 0.0,
    #            "ETHbinAUD": 0.0,
    #            "ETHbtcmAUD": 49909.26,
    #            "LTCbinAUD": 0.52,
    #            "LTCbtcmAUD": 0.0,
    #            "XRPbinAUD": 2.96,
    #            "XRPbtcmAUD": 0.0
    #        },
    #        "KM-PORTFOLIO-SUM": {
    #            "profitPercent": 68.7,
    #            "totalALL": 77590.47,
    #            "totalBINalt": 6484.1,
    #            "totalBINmain": 847.42,
    #            "totalBTCMmain": 70258.95,
    #            "totalCashIn": 46000.0,
    #            "totalProfit": 31590.47
    #        },
    #        "kCryptoDictType": "portfolio"
    #    }
    myPortfolioStartTime = time.time()

  #READ GSHEET RANGE CONTAINING MAINSTREAM COINS-----------------------------------
    gSheetBlockMainCoins = _GOOGLE._readFromGoogleSheet('[CryptoSum]!B8:Q14')

    #ITERATE THROUGH THE RANGE, EXTRACTING RELEVANT VALUES, PLACING THEM IN JSON DICTIONARY
    portValDictOuter = {"kCryptoDictType": 'portfolio'}
    portValDictOuter.update ({"zzPortfolioTime":  time.time() - myPortfolioStartTime})
    portValDictInner = {}
    for row in gSheetBlockMainCoins:
        coin    = row[0]
        btcmVal = float(row[9])
        portValDictInner.update( {coin + "btcmAUD":  btcmVal, } )
        if coin != "AUD":   #DONT ATTEMPT TO FIND AUD IN BINANCE... ITS NOT THERE
            binVal  = float(row[14])
            portValDictInner.update( {coin + "binAUD":  binVal, } )
    portValDictOuter.update( {"KM-PORTFOLIO" : portValDictInner, } )

 #READ GSHEET RANGE CONTAINING SUMMARY----------------------------------------------
    gSheetBlockSumList = _GOOGLE._readFromGoogleSheet('[CryptoSum]!K16:X20')

    #ITERATE THROUGH THE RANGE, EXTRACTING RELEVANT VALUES, PLACING THEM IN JSON DICTIONARY
    portSumDictInner = {}

    totalBTCMmain   = float(gSheetBlockSumList[0][0])
    totalBINmain    = float(gSheetBlockSumList[0][5])
    totalBINalt     = float(gSheetBlockSumList[1][5])
    totalALL        = float(gSheetBlockSumList[1][0])
    totalCashIn     = float(gSheetBlockSumList[2][0])
    totalProfit     = float(gSheetBlockSumList[3][0])
    profitPercent   = float(gSheetBlockSumList[4][0])

    portSumDictInner.update( {"totalBTCMmain": totalBTCMmain, "totalBINmain": totalBINmain, "totalBINalt": totalBINalt, "totalALL": totalALL, "totalCashIn": totalCashIn, "totalProfit": totalProfit, "profitPercent": profitPercent,} )
    portValDictOuter.update( {"KM-PORTFOLIO-SUM" : portSumDictInner, } )

  #SPIT THE PORTFOLIO VALUES TO SPLUNK
    _OUTPUT._spitJSONoutToSplunk(portValDictOuter)

    return

def _thresholdOps():
    #BTCM
    googleSheetBlock = _GOOGLE._readFromGoogleSheet('[CryptoSum]!B8:G13')
    _BTCMARKETS._resetAlert_btcmTicker(googleSheetBlock)
    _BTCMARKETS._breachCheck_btcmTicker(googleSheetBlock)
    return

def _timestampGsheet():
    timeList            = [ [ strftime("%d/%m/%Y %H:%M:%S"), ], ]
    _GOOGLE._publishToGoogleSheet(timeList,         'USER_ENTERED', '[CryptoSum]!C25',          'COLUMNS')
    return


#---------------------------------------------------------------------------------------------------------------------------------------------------
# MAIN CODE INVOKE POINT
#---------------------------------------------------------------------------------------------------------------------------------------------------
_main()

#---------------------------------------------------------------------------------------------------------------------------------------------------
# JSON DATA STRUCTURES
#---------------------------------------------------------------------------------------------------------------------------------------------------
'''

    ################################### BTCM TICKER
    {
        u'bestBid': 20484.99,
        u'lastPrice': 20500.0,
        u'instrument': u'BTC',
        u'timestamp': 1514001595,
        u'volume24h': 1832.4491,
        u'currency': u'AUD',
        u'bestAsk': 20499.0
    }


    ################################### BTCM ACCOUNT BALANCES
    [
        {
            u'currency': u'AUD',
            u'pendingFunds': 0,
            u'balance': 2
        },
        {
            u'currency': u'BTC',
            u'pendingFunds': 0,
            u'balance': 61699334
        },
        ......,
    ]

    ################################### BINANCE TICKER
    [
        {
            "symbol":"ETHBTC",
            "price":"0.05129200"
        },
        {
            "symbol":"LTCBTC",
            "price":"0.01656800"
        },
        {
            "symbol":"BNBBTC",
            "price":"0.00060960"
        },
        {
            "symbo.........

    ################################### BINANCE ACCOUNT BALANCES
        {

          u'balances': [
            {
              u'locked': u'0.00000000',
              u'asset': u'BTC',
              u'free': u'0.00007391'
            },
            {
              u'locked': u'0.00000000',
              u'asset': u'LTC',
              u'free': u'0.00151646'
            },
            ...... x like 100!!
          ],
          u'sellerCommission': 0,
          u'canDeposit': True
          u'buyerCommission': 0,
          u'updateTime': 1513737345672,
          u'canWithdraw': True,
          u'takerCommission': 10,
          u'canTrade': True,
          u'makerCommission': 10,
        }


    ################################### NANOPOOL
        {
            "status": true,
            "data": {
                "account": "0x529640368fd1bc2637258ab6991e5db3a2822e32",
                "unconfirmed_balance": "0.00000000",
                "balance": "0.02502008",
                "hashrate": "187.0",
                "avgHashrate": {
                    "h1": "164.3",
                    "h3": "146.4",
                    "h6": "151.3",
                    "h12": "155.7",
                    "h24": "150.9"
                },
                "workers": [
                    {
                        "id": "rig1",
                        "uid": 1799722,
                        "hashrate": "127.5",
                        "lastshare": 1514074927,
                        "rating": 26503,
                        "h1": "164.3",
                        "h3": "146.4",
                        "h6": "151.3",
                        "h12": "155.7",
                        "h24": "150.9"
                    }
            }
        }




'''
