########################################
# VERSION:  1.2
# UPDATED:  27/12/2018
# DESCRIP:  scripted inputs for bex36 splunk weather
# NOTES:
########################################

import sys 				                 #for sys.stdout.write(plusCurlList)
import datetime  		                 #to convert epoch to human readable
import urllib, json
import urllib2
import time  			                #TO MEASURE EXECUTION TIMES
import socket			                #FOR DNS OPERATIONS
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET      #FOR XML PARSING

#GIT TEST

#GLOBAL VARIABLES
myProgStartTime = time.time()

def _main():
    scriptStartTime = time.time()

    #INITIALISE THE DICTS
    bomCurDict = {}
    bomFutDict = {}

    #GET CURRENT BOM DATA
#    bomCurDict = _collectBOMcurJSON(bomCurDict)
#    _spitJSONoutToSplunk(bomCurDict)

    #GET FUTURE BOM DATA
    bomFutDict = _collectBOMpredXML(bomFutDict)
    _spitJSONoutToSplunk(bomFutDict)

    scriptRunTime = {"ScriptRunTime_GETWEATHER.py":  time.time() - scriptStartTime}
    _spitJSONoutToSplunk(scriptRunTime)


def _logToFile():
	f = open('/_LOCALDATA/_PROGDATA/SCRIPTS/_LOGS/ksplunkscriptedinput.log', 'a')
	f.write('hi there myProgStartTime: ' + str(datetime.datetime.fromtimestamp(myProgStartTime).strftime('%c')) + '\n')  # python will convert \n to os.linesep
	f.close()  # you can omit in most cases as the destructor will call it


#---------------------------------------------------------------------------------------------------------------------------------------------------
def _collectBOMpredXML(myDict):
    myBOMStartTime = time.time()

    url = "ftp://ftp.bom.gov.au/anon/gen/fwo/IDN10064.xml"

###################
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req)
    tree = ET.fromstring(page.read())
#    print (tree)
#    root = tree.getroot()
#    tree.attrib

#    for child in tree:
#        print(child.tag, child.attrib)

#    for xxx in tree.iter('area'):
#        print(xxx.attrib)
#    show(tree)
#    print myList
########################
#    myList = tree.findall("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='1']")
#    print myList[0].attrib['start-time-local']
#    for xxx in myList:
#        print xxx.attrib['start-time-local']
###########################
#    for node in tree:
#        print node

    resultsDict = {"BOMxmlDlTime": time.time() - myBOMStartTime}

    resultsDict.update( {"BOMPREDiconCode":     int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='1']/element/[@type='forecast_icon_code']").text) } )
    resultsDict.update( {"BOMPREDtempMax":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='1']/element/[@type='air_temperature_maximum']").text) } )
    resultsDict.update( {"BOMPREDtempMin":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='1']/element/[@type='air_temperature_minimum']").text) } )
    resultsDict.update( {"BOMPREDrainChance":   int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='1']/text/[@type='probability_of_precipitation']").text.rstrip('%')) } )
    resultsDict.update( {"BOMPREDdesc":         tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='1']/text/[@type='precis']").text } )


    myDict.update(resultsDict)
    return myDict

def show(elem):
    print elem.tag
    for child in elem.findall('*'):
        show(child)




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
