########################################
# VERSION:  1.2
# UPDATED:  29/12/2018
# DESCRIP:  scripted inputs for bex36 splunk weather - CURRENT/OBSERVATIONS
# NOTES:
########################################

import sys 				                 #for sys.stdout.write(plusCurlList)
import datetime  		                 #to convert epoch to human readable
import urllib, json
import urllib2
import time  			                #TO MEASURE EXECUTION TIMES
import socket			                #FOR DNS OPERATIONS
from subprocess import Popen, PIPE

#GLOBAL VARIABLES
myProgStartTime = time.time()

def _main():
    scriptStartTime = time.time()

    #INITIALISE THE DICTS
    bomCurDict = {}

    #GET CURRENT BOM DATA
    bomCurDict = _collectBOMcurJSON(bomCurDict)
    _spitJSONoutToSplunk(bomCurDict)


    scriptRunTime = {"ScriptRunTime_GETWEATHER.py":  time.time() - scriptStartTime}
    _spitJSONoutToSplunk(scriptRunTime)


def _logToFile():
	f = open('/_LOCALDATA/_PROGDATA/SCRIPTS/_LOGS/ksplunkscriptedinput.log', 'a')
	f.write('hi there myProgStartTime: ' + str(datetime.datetime.fromtimestamp(myProgStartTime).strftime('%c')) + '\n')  # python will convert \n to os.linesep
	f.close()  # you can omit in most cases as the destructor will call it




#---------------------------------------------------------------------------------------------------------------------------------------------------
def _collectBOMcurJSON(myDict):
    myBOMStartTime = time.time()
    # NOTE: for non-JSON, view: http://www.bom.gov.au/products/IDN60901/IDN60901.94765.shtml

    #BANKSTOWN (all metrics at every interval)
    url = "http://www.bom.gov.au/fwo/IDN60901/IDN60901.94765.json"
    #SYDNEY AIRPOT (SOME METRICS [temp+humidity] AVAILABLE AT ONLY: 0600,0900,1200,1500,1800)
    #url = "http://www.bom.gov.au/fwo/IDN60801/IDN60801.94767.json"


################### NEW
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req)
    content = page.read()
    data = json.loads(content)
################### OLD
    #OPEN URL AND BUILD PYTHON-DICT BASED ON JSON REPONSE DATA
#    response = urllib.urlopen(url)
#    print response.read()
#    data = json.loads(response.read())
#    print (data)
    #	myList.append("BOMjsonDlTime=" + str(time.time() - myBOMStartTime))

    resultsDict = {"BOMjsonDlTime": time.time() - myBOMStartTime}
    resultsDict.update( {"kCryptoDictType": 'BOMobservations'} )

    #METRICS AVAILABLE FOR EVERY POLL
    resultsDict.update( {"BOMdateTime":     float(data['observations']['data'][0]['local_date_time_full']) } )
    resultsDict.update( {"BOMcloud":        data['observations']['data'][0]['cloud'] } )
    resultsDict.update( {"BOMwindDir":      data['observations']['data'][0]['wind_dir'] } )
    resultsDict.update( {"BOMwindSpd":      data['observations']['data'][0]['wind_spd_kmh'] } )
    resultsDict.update( {"BOMwindGst":      data['observations']['data'][0]['gust_kmh'] } )
    resultsDict.update( {"BOMrain":         float(data['observations']['data'][0]['rain_trace']) } )
    resultsDict.update( {"BOMpress":        data['observations']['data'][0]['press'] } )
    #if i choose syndey airport (94767) the below only delivered at 0600,0900,1200,1500,1800)
    resultsDict.update( {"BOMhumid":        data['observations']['data'][0]['rel_hum'] } )
    resultsDict.update( {"BOMtempAir":      data['observations']['data'][0]['air_temp'] } )
    resultsDict.update( {"BOMtempFeel":     data['observations']['data'][0]['apparent_t'] } )
    #added dewpoint 20170522
    resultsDict.update( {"BOMdewpt":        data['observations']['data'][0]['dewpt'] } )
    resultsDict.update( {"BOMcloud":        data['observations']['data'][0]['cloud'] } )

    myDict.update(resultsDict)
    return myDict


#---------------------------------------------------------------------------------------------------------------------------------------------------
def _spitJSONoutToSplunk(myDict):
    print (json.dumps(myDict, indent=4, sort_keys=True))


#MAIN CODE INVOKE POINT
_main()
