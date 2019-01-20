import time  			#TO MEASURE EXECUTION TIMES,
import urllib2          #FOR CONNECTING TO NANOPOOL, WHICH HAS A MORE SOPHISTICATED API
import json             #FOR JSON OPERATIONS

import sys
sys.path.append('/_LOCALDATA/_PROGDATA/SCRIPTS/_CONFIG')
import _CRYPTOCONFIG
import _OUTPUT
import _GOOGLE

#K GLOBAL VARIABLES
walletAddrETH       = _CRYPTOCONFIG.NANOwalAddrETH

#---------------------------------------------------------------------------------------------------------------------------------------------------
# NANOPOOL FUNCTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------
def _collectNANOPOOLdata():
    myNANOStartTime = time.time()

    ## NANOPOOL API doco is here:  https://eth.nanopool.org/api
    url = "https://api.nanopool.org/v1/eth/user/" + walletAddrETH
    #OPEN URL AND BUILD PYTHON-DICT BASED ON JSON REPONSE DATA
    #NANOPOOL API WONT LET YOU HIT IT WITHOUT HEADERS.... I WIRESHARKED MY CHROME
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}

    #HEADERS REQUIRES REVISED URL APPROACH
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req)
    content = page.read()
    resultsDict = json.loads(content)
#    _OUTPUT._spitJSONoutToSplunk(resultsDict)
    #when it fails (as it frequently does, shitty API) resultsDict = {"status":false,"error":"No data found"}
    if not resultsDict['status']:
        myNanoDict = {"ERROR":                      "nanopool API fail"}
        myNanoDict.update( {"status":               resultsDict['status']} )
    else:
        myNanoDict = {"zzNANOPjsonDlTime":          time.time() - myNANOStartTime}
        myNanoDict.update( {"ETHwallAddr":          resultsDict['data']['account']} )
        myNanoDict.update( {"ETHminingBal":         float(resultsDict['data']['balance']) } )
        myNanoDict.update( {"hashRate":             float(resultsDict['data']['hashrate']) } )
        myNanoDict.update( {"hashRate1hrAvg":       float(resultsDict['data']['avgHashrate']['h1']) } )
#2018.01.20: COMMENTING OUT THE BELOW WHILE RIG IS OFF AS OTHERWISE IT THROWS ERROR, AS 'workers' IN THE JSON IS AN EMPTY LIST. UNCOMMENT THE ABOVE TO CONFIRM WHEN RETESTING: _OUTPUT._spitJSONoutToSplunk(resultsDict)  
#        myNanoDict.update( {"rig1hashRate":         float(resultsDict['data']['workers'][0]['hashrate']) } )
#        myNanoDict.update( {"rig1hashRate1hrAvg":   float(resultsDict['data']['workers'][0]['h1']) } )
#        myNanoDict.update( {"rig1lastShare":        float(resultsDict['data']['workers'][0]['lastshare']) } )
        myNanoDict.update( {"status":               resultsDict['status']} )
    return myNanoDict

def _nanoPoolOps():
    nanoDict = {"NanoPool": _collectNANOPOOLdata()}
    nanoDict.update( {"kCryptoDictType": 'nanopool'} )
    _OUTPUT._spitJSONoutToSplunk(nanoDict)
    if nanoDict['NanoPool']['status']:
        nanoValues = [ [ nanoDict['NanoPool']['ETHminingBal'], ], ]
        _GOOGLE._publishToGoogleSheet(nanoValues,'USER_ENTERED','[CryptoSum]!C21',      'COLUMNS')
    return
