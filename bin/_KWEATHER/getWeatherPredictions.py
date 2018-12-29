########################################
# VERSION:  1.2
# UPDATED:  29/12/2018
# DESCRIP:  scripted inputs for bex36 splunk weather - FUTURE/PREDCTIONS
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

#GLOBAL VARIABLES
myProgStartTime = time.time()

def _main():
    scriptStartTime = time.time()

    #INITIALISE THE DICTS
    bomFutDict = {}

    #GET FUTURE BOM DATA
    bomFutDict = _collectBOMpredXML(bomFutDict)
    _spitJSONoutToSplunk(bomFutDict)

    scriptRunTime = {"ScriptRunTime_GETWEATHERPREDICTIONS.py":  time.time() - scriptStartTime}
    _spitJSONoutToSplunk(scriptRunTime)


def _logToFile():
	f = open('/_LOCALDATA/_PROGDATA/SCRIPTS/_LOGS/ksplunkscriptedinput.log', 'a')
	f.write('hi there myProgStartTime: ' + str(datetime.datetime.fromtimestamp(myProgStartTime).strftime('%c')) + '\n')  # python will convert \n to os.linesep
	f.close()  # you can omit in most cases as the destructor will call it


#---------------------------------------------------------------------------------------------------------------------------------------------------
def _collectBOMpredXML(myDict):
    myBOMStartTime = time.time()
    url = "ftp://ftp.bom.gov.au/anon/gen/fwo/IDN10064.xml"
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    req = urllib2.Request(url, headers=hdr)
    page = urllib2.urlopen(req)
    tree = ET.fromstring(page.read())

    resultsDict = {"BOMxmlDlTime": time.time() - myBOMStartTime}
    resultsDict.update( {"kCryptoDictType": 'BOMpredictions'} )
    #resultsDict.update( {"TODAY-PLUS-0":   _extractDayPrediction(tree,0) } )
    #resultsDict.update( {"TODAY-PLUS-1":   _extractDayPrediction(tree,1) } )
    #resultsDict.update( {"TODAY-PLUS-2":   _extractDayPrediction(tree,2) } )
    #resultsDict.update( {"TODAY-PLUS-3":   _extractDayPrediction(tree,3) } )
    #resultsDict.update( {"TODAY-PLUS-4":   _extractDayPrediction(tree,4) } )
    #resultsDict.update( {"TODAY-PLUS-5":   _extractDayPrediction(tree,5) } )
    #resultsDict.update( {"TODAY-PLUS-6":   _extractDayPrediction(tree,6) } )

    _extractDayPrediction(tree,0)
    _extractDayPrediction(tree,1)
    _extractDayPrediction(tree,2)
    _extractDayPrediction(tree,3)
    _extractDayPrediction(tree,4)
    _extractDayPrediction(tree,5)
    _extractDayPrediction(tree,6)


    #SOMETIMES THERE IS 7, SOMETIMES NOT... I THINK IN THE ARVO THERE IT BECOMES AVAILABLE.... BETTER TO LIVE WITHOUT
    #resultsDict.update( {"TODAY-PLUS-7":   _extractDayPrediction(tree,7) } )

    myDict.update(resultsDict)
    return myDict

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _extractDayPrediction(tree, dayIndex):
    resultsDict = {}

    #XML FOR TODAY IS DIFFERENT
    if dayIndex == 0:
        resultsDict.update( {"BOMPREDdate":         tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']").attrib['start-time-local'] } )   #[:-15] to trim the 15 chars off the date 'T00:00:00+11:00'
        resultsDict.update( {"BOMPREDiconCode":     int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='forecast_icon_code']").text) } )
        resultsDict.update( {"BOMPREDrainChance":   int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='probability_of_precipitation']").text.rstrip('%')) } )
        resultsDict.update( {"BOMPREDdescBrief":    tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='precis']").text } )
        #THE BELOW COMES FROM THE PARENT XML NSW_ME001
        resultsDict.update( {"BOMPREDdescDetail":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='forecast']").text } )
    elif dayIndex == 1:
        resultsDict.update( {"BOMPREDsurfDanger":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='surf_danger']").text } )
        resultsDict.update( {"BOMPREDfireDanger":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='fire_danger']").text } )
        resultsDict.update( {"BOMPREDuvAlert":      tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='uv_alert']").text } )

        resultsDict.update( {"BOMPREDdate":         tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']").attrib['start-time-local'] } )   #[:-15] to trim the 15 chars off the date 'T00:00:00+11:00'
        resultsDict.update( {"BOMPREDiconCode":     int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='forecast_icon_code']").text) } )
        resultsDict.update( {"BOMPREDtempMax":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='air_temperature_maximum']").text) } )
        resultsDict.update( {"BOMPREDrainChance":   int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='probability_of_precipitation']").text.rstrip('%')) } )
        resultsDict.update( {"BOMPREDdescBrief":    tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='precis']").text } )
        resultsDict.update( {"BOMPREDtempMin":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='air_temperature_minimum']").text) } )
        #THE BELOW COMES FROM THE PARENT XML NSW_ME001
        resultsDict.update( {"BOMPREDdescDetail":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='forecast']").text } )
    else:
        resultsDict.update( {"BOMPREDdate":         tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']").attrib['start-time-local'] } )   #[:-15] to trim the 15 chars off the date 'T00:00:00+11:00'
        resultsDict.update( {"BOMPREDiconCode":     int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='forecast_icon_code']").text) } )
        resultsDict.update( {"BOMPREDtempMax":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='air_temperature_maximum']").text) } )
        resultsDict.update( {"BOMPREDrainChance":   int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='probability_of_precipitation']").text.rstrip('%')) } )
        resultsDict.update( {"BOMPREDdescBrief":    tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='precis']").text } )
        resultsDict.update( {"BOMPREDtempMin":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='air_temperature_minimum']").text) } )
        #THE BELOW COMES FROM THE PARENT XML NSW_ME001
        resultsDict.update( {"BOMPREDdescDetail":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='forecast']").text } )

    #NEED TO SPIT LINE BY LINE TO GET SEPERATE SPLUNK EVEMNTS
    _spitJSONoutToSplunk(resultsDict)
    return

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _extractDayPredictionORIG(tree, dayIndex):
    resultsDict = {}
    resultsDict.update( {"BOMPREDdate":         tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']").attrib['start-time-local'][:-15] } )   #[:-15] to trim the 15 chars off the date 'T00:00:00+11:00'
    resultsDict.update( {"BOMPREDiconCode":     int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='forecast_icon_code']").text) } )
    resultsDict.update( {"BOMPREDtempMax":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='air_temperature_maximum']").text) } )
    resultsDict.update( {"BOMPREDrainChance":   int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='probability_of_precipitation']").text.rstrip('%')) } )
    resultsDict.update( {"BOMPREDdescBrief":    tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='precis']").text } )
    #THE BELOW COMES FROM THE PARENT XML NSW_ME001
    resultsDict.update( {"BOMPREDdescDetail":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)        + "']/text/[@type='forecast']").text } )

    #XML FOR TODAY IS DIFFERENT
    if dayIndex == 0:
        resultsDict.update( {"BOMPREDsurfDanger":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='surf_danger']").text } )
        resultsDict.update( {"BOMPREDfireDanger":   tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='fire_danger']").text } )
        resultsDict.update( {"BOMPREDuvAlert":      tree.find("./forecast/area/[@aac='NSW_ME001']/forecast-period/[@index='" + str(dayIndex)    + "']/text/[@type='uv_alert']").text } )
    else:
        resultsDict.update( {"BOMPREDtempMin":      int(tree.find("./forecast/area/[@aac='NSW_PT131']/forecast-period/[@index='" + str(dayIndex)    + "']/element/[@type='air_temperature_minimum']").text) } )

    #NEED TO SPIT LINE BY LINE TO GET SEPERATE SPLUNK EVEMNTS
    _spitJSONoutToSplunk(resultsDict)
    return

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _spitJSONoutToSplunk(myDict):
    print (json.dumps(myDict, indent=4, sort_keys=True))


#MAIN CODE INVOKE POINT
_main()



#---------------------------------------------------------------------------------------------------------------------------------------------------
# EXAMPLE XML DATA STRUCTURE - TAKEN ON 2018-12-29
#---------------------------------------------------------------------------------------------------------------------------------------------------
'''
<product xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" version="1.7" xsi:noNamespaceSchemaLocation="http://www.bom.gov.au/schema/v1.7/product.xsd">
    <amoc>...</amoc>
    <forecast>
    <area aac="NSW_FA001" description="New South Wales" type="region">...</area>
    <area aac="NSW_ME001" description="Sydney" type="metropolitan" parent-aac="NSW_FA001">
        <forecast-period index="0" start-time-local="2018-12-29T00:00:00+11:00" end-time-local="2018-12-30T00:00:00+11:00" start-time-utc="2018-12-28T13:00:00Z" end-time-utc="2018-12-29T13:00:00Z">
            <text type="forecast">
            Hot and sunny. Winds north to northwesterly 15 to 20 km/h turning northeasterly 25 to 35 km/h in the early afternoon then decreasing to 15 to 20 km/h in the late evening.
            </text>
            <text type="surf_danger">
            A POOR Air Quality Forecast alert is issued by the Office of Environment and Heritage due to elevated OZONE pollution in Sydney for today.
            </text>
            <text type="fire_danger">Very High</text>
            <text type="uv_alert">
            Sun protection 8:30am to 5:20pm, UV Index predicted to reach 13 [Extreme]
            </text>
        </forecast-period>
        <forecast-period index="1" start-time-local="2018-12-30T00:00:00+11:00" end-time-local="2018-12-31T00:00:00+11:00" start-time-utc="2018-12-29T13:00:00Z" end-time-utc="2018-12-30T13:00:00Z">
            <text type="forecast">
            Hot and mostly sunny. Winds northeasterly 15 to 20 km/h tending north to northwesterly in the morning then tending northeasterly 20 to 30 km/h in the late afternoon.
            </text>
        </forecast-period>
        <forecast-period index="2" start-time-local="2018-12-31T00:00:00+11:00" end-time-local="2019-01-01T00:00:00+11:00" start-time-utc="2018-12-30T13:00:00Z" end-time-utc="2018-12-31T13:00:00Z">
            <text type="forecast">
            Partly cloudy. Medium (40%) chance of showers, most likely in the afternoon and evening. The chance of a thunderstorm in the afternoon and evening. Light winds.
            </text>
            </forecast-period>
        <forecast-period index="3" start-time-local="2019-01-01T00:00:00+11:00" end-time-local="2019-01-02T00:00:00+11:00" start-time-utc="2018-12-31T13:00:00Z" end-time-utc="2019-01-01T13:00:00Z">
            <text type="forecast">
            Partly cloudy. Slight (20%) chance of a shower or storm, most likely in the afternoon and evening. Light winds.
            </text>
        </forecast-period>
        <forecast-period index="4" start-time-local="2019-01-02T00:00:00+11:00" end-time-local="2019-01-03T00:00:00+11:00" start-time-utc="2019-01-01T13:00:00Z" end-time-utc="2019-01-02T13:00:00Z">
            <text type="forecast">
            Partly cloudy. Slight (30%) chance of a shower. Light winds becoming east to northeasterly 15 to 20 km/h during the day.
            </text>
        </forecast-period>
        <forecast-period index="5" start-time-local="2019-01-03T00:00:00+11:00" end-time-local="2019-01-04T00:00:00+11:00" start-time-utc="2019-01-02T13:00:00Z" end-time-utc="2019-01-03T13:00:00Z">
            <text type="forecast">
            Partly cloudy. Medium (40%) chance of showers, most likely later in the day. The chance of a thunderstorm later in the day. Winds northeasterly 15 to 25 km/h.
            </text>
        </forecast-period>
        <forecast-period index="6" start-time-local="2019-01-04T00:00:00+11:00" end-time-local="2019-01-05T00:00:00+11:00" start-time-utc="2019-01-03T13:00:00Z" end-time-utc="2019-01-04T13:00:00Z">
            <text type="forecast">
            Partly cloudy. Slight (30%) chance of a shower, most likely during the morning. Winds north to northeasterly 15 to 20 km/h tending southeast to southwesterly later.
            </text>
        </forecast-period>
    </area>
    <area aac="NSW_PT131" description="Sydney" type="location" parent-aac="NSW_ME001">
        <forecast-period index="0" start-time-local="2018-12-29T09:27:13+11:00" end-time-local="2018-12-30T00:00:00+11:00" start-time-utc="2018-12-28T22:27:13Z" end-time-utc="2018-12-29T13:00:00Z">
            <element type="forecast_icon_code">1</element>
            <element type="air_temperature_maximum" units="Celsius">30</element>
            <text type="precis">Sunny.</text>
            <text type="probability_of_precipitation">0%</text>
        </forecast-period>
        <forecast-period index="1" start-time-local="2018-12-30T00:00:00+11:00" end-time-local="2018-12-31T00:00:00+11:00" start-time-utc="2018-12-29T13:00:00Z" end-time-utc="2018-12-30T13:00:00Z">
            <element type="forecast_icon_code">3</element>
            <element type="air_temperature_minimum" units="Celsius">22</element>
            <element type="air_temperature_maximum" units="Celsius">31</element>
            <text type="precis">Mostly sunny.</text>
            <text type="probability_of_precipitation">5%</text>
        </forecast-period>
        <forecast-period index="2" start-time-local="2018-12-31T00:00:00+11:00" end-time-local="2019-01-01T00:00:00+11:00" start-time-utc="2018-12-30T13:00:00Z" end-time-utc="2018-12-31T13:00:00Z">
            <element type="forecast_icon_code">17</element>
            <element type="precipitation_range">0 to 0.4 mm</element>
            <element type="air_temperature_minimum" units="Celsius">22</element>
            <element type="air_temperature_maximum" units="Celsius">31</element>
            <text type="precis">Possible shower.</text>
            <text type="probability_of_precipitation">40%</text>
        </forecast-period>
        <forecast-period index="3" start-time-local="2019-01-01T00:00:00+11:00" end-time-local="2019-01-02T00:00:00+11:00" start-time-utc="2018-12-31T13:00:00Z" end-time-utc="2019-01-01T13:00:00Z">
            <element type="forecast_icon_code">3</element>
            <element type="air_temperature_minimum" units="Celsius">22</element>
            <element type="air_temperature_maximum" units="Celsius">29</element>
            <text type="precis">Mostly sunny.</text>
            <text type="probability_of_precipitation">10%</text>
        </forecast-period>
        <forecast-period index="4" start-time-local="2019-01-02T00:00:00+11:00" end-time-local="2019-01-03T00:00:00+11:00" start-time-utc="2019-01-01T13:00:00Z" end-time-utc="2019-01-02T13:00:00Z">
            <element type="forecast_icon_code">3</element>
            <element type="air_temperature_minimum" units="Celsius">22</element>
            <element type="air_temperature_maximum" units="Celsius">30</element>
            <text type="precis">Partly cloudy.</text>
            <text type="probability_of_precipitation">20%</text>
        </forecast-period>
        <forecast-period index="5" start-time-local="2019-01-03T00:00:00+11:00" end-time-local="2019-01-04T00:00:00+11:00" start-time-utc="2019-01-02T13:00:00Z" end-time-utc="2019-01-03T13:00:00Z">
            <element type="forecast_icon_code">17</element>
            <element type="precipitation_range">0 to 1 mm</element>
            <element type="air_temperature_minimum" units="Celsius">22</element>
            <element type="air_temperature_maximum" units="Celsius">32</element>
            <text type="precis">Possible late shower.</text>
            <text type="probability_of_precipitation">40%</text>
        </forecast-period>
        <forecast-period index="6" start-time-local="2019-01-04T00:00:00+11:00" end-time-local="2019-01-05T00:00:00+11:00" start-time-utc="2019-01-03T13:00:00Z" end-time-utc="2019-01-04T13:00:00Z">
            <element type="forecast_icon_code">3</element>
            <element type="precipitation_range">0 to 0.4 mm</element>
            <element type="air_temperature_minimum" units="Celsius">22</element>
            <element type="air_temperature_maximum" units="Celsius">31</element>
            <text type="precis">Partly cloudy.</text>
            <text type="probability_of_precipitation">30%</text>
        </forecast-period>
        </area>
    <area aac="NSW_PT114" description="Penrith" type="location" parent-aac="NSW_ME001">...</area>
'''
