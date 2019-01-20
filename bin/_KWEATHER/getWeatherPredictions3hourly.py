########################################
# VERSION:  1.0
# UPDATED:  13/01/2019
########################################
'''
K-NOTE: THIS CODE RELIES ON
  - 'BEAUTIFUL SOUP' (HTML DATA EXTRACTION).... Doco for beaut soup here: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
  - LXML (PARSER).
  INSTALL THEM WITH 'sudo pip install beautifulsoup4' and 'sudo pip install lxml'  <<< SUDO is important!!
'''
import sys 				                 #for sys.stdout.write(plusCurlList)
import datetime  		                 #to convert epoch to human readable
import urllib, json
import urllib2
import time  			                #TO MEASURE EXECUTION TIMES
import socket			                #FOR DNS OPERATIONS
from subprocess import Popen, PIPE
import xml.etree.ElementTree as ET      #FOR XML PARSING

from bs4 import BeautifulSoup
import re


#GLOBAL VARIABLES
myProgStartTime = time.time()

def _main():
    scriptStartTime = time.time()

    #INITIALISE THE DICTS
    bomFut3hrDict = {}

    #GET FUTURE BOM DATA
    bomFut3hrDict = _collectBOMpred3hr(bomFut3hrDict)
    _spitJSONoutToSplunk(bomFut3hrDict)

    scriptRunTime = {"ScriptRunTime_GETWEATHERPREDICTIONS3HOURLY.py":  time.time() - scriptStartTime}
    _spitJSONoutToSplunk(scriptRunTime)


def _logToFile():
	f = open('/_LOCALDATA/_PROGDATA/SCRIPTS/_LOGS/ksplunkscriptedinput.log', 'a')
	f.write('hi there myProgStartTime: ' + str(datetime.datetime.fromtimestamp(myProgStartTime).strftime('%c')) + '\n')  # python will convert \n to os.linesep
	f.close()  # you can omit in most cases as the destructor will call it


#---------------------------------------------------------------------------------------------------------------------------------------------------
#VERY LAZY CODE IN HERE>.. COME BACK TO IT AND MAKE IT LOOPS...
def _collectBOMpred3hr(myDict):
    myBOMStartTime = time.time()
    url = "http://www.bom.gov.au/places/nsw/sydney/forecast/detailed/"
    hdr = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.84 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
    request  = urllib2.Request(url, headers=hdr)
    response = urllib2.urlopen(request)
    html = response.read()
    soup = BeautifulSoup(html, features="lxml")   #lxml is much better than 'features="html.parser"' according to B.S. doco'

    now = datetime.datetime.now()
    tmr = now + datetime.timedelta(days=1)
    plsTwo = now + datetime.timedelta(days=2)
    plsThree = now + datetime.timedelta(days=3)
    plsFour = now + datetime.timedelta(days=4)
    plsFive = now + datetime.timedelta(days=5)
    plsSix = now + datetime.timedelta(days=6)

    dateToday       = str(now.strftime('%Y')) + "-" + str(now.strftime('%m')) + "-" + str(now.strftime('%d'))   #needs to look like: 'd2019-01-13'
    dateTmr         = str(tmr.strftime('%Y')) + "-" + str(tmr.strftime('%m')) + "-" + str(tmr.strftime('%d'))   #needs to look like: 'd2019-01-13'
    datePlsTwo      = str(plsTwo.strftime('%Y')) + "-" + str(plsTwo.strftime('%m')) + "-" + str(plsTwo.strftime('%d'))   #needs to look like: 'd2019-01-13'
    datePlsThree    = str(plsThree.strftime('%Y')) + "-" + str(plsThree.strftime('%m')) + "-" + str(plsThree.strftime('%d'))
    datePlsFour     = str(plsFour.strftime('%Y')) + "-" + str(plsFour.strftime('%m')) + "-" + str(plsFour.strftime('%d'))
    datePlsFive     = str(plsFive.strftime('%Y')) + "-" + str(plsFive.strftime('%m')) + "-" + str(plsFive.strftime('%d'))
    datePlsSix      = str(plsSix.strftime('%Y')) + "-" + str(plsSix.strftime('%m')) + "-" + str(plsSix.strftime('%d'))

    #TODAY
    listRainMM_tdy =        _scrapeHTML(soup, dateToday, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_tdy =    _scrapeHTML(soup, dateToday, 'Rainfall', 'Chance of any rain')
    listTempFeel_tdy =      _scrapeHTML(soup, dateToday, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_tdy =            _scrapeHTML(soup, dateToday, 'UV', 'UV Index')
    listStorms_tdy =        _scrapeHTML(soup, dateToday, 'Significant Weather', 'Thunderstorms')
    listHumid_tdy =        _scrapeHTML(soup, dateToday, re.compile('Humidity '), re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly

#WIND SPEED IS A BASTARD, AS THE BOM CODERS MESSED UP THE HTML. SO THIS IS NOT YET WORKING.... SEE BELOW 'THIS NEXT LINE IS SCREWED' IN THEW HTML
#    listWindSp_tdy =        _scrapeHTML(soup, dateToday, re.compile('Humidity '), 'Wind speed')   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly
#    print (listWindSp_tdy)

    #TOMORROW
    listRainMM_tmr =        _scrapeHTML(soup, dateTmr, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_tmr =    _scrapeHTML(soup, dateTmr, 'Rainfall', 'Chance of any rain')
    listTempFeel_tmr =      _scrapeHTML(soup, dateTmr, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_tmr =            _scrapeHTML(soup, dateTmr, 'UV', 'UV Index')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listStorms_tmr =        _scrapeHTML(soup, dateTmr, 'Significant Weather', 'Thunderstorms')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listHumid_tmr =        _scrapeHTML(soup, dateTmr, 'Humidity & Wind', re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly

    #DAY AFTER TOMORROW
    listRainMM_plsTwo =        _scrapeHTML(soup, datePlsTwo, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_plsTwo =    _scrapeHTML(soup, datePlsTwo, 'Rainfall', 'Chance of any rain')
    listTempFeel_plsTwo =      _scrapeHTML(soup, datePlsTwo, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_plsTwo =            _scrapeHTML(soup, datePlsTwo, 'UV', 'UV Index')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listStorms_plsTwo =        _scrapeHTML(soup, datePlsTwo, 'Significant Weather', 'Thunderstorms')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listHumid_plsTwo =        _scrapeHTML(soup, datePlsTwo, 'Humidity & Wind', re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly

    #DAY PLUS THREE
    listRainMM_plsThree =        _scrapeHTML(soup, datePlsThree, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_plsThree =    _scrapeHTML(soup, datePlsThree, 'Rainfall', 'Chance of any rain')
    listTempFeel_plsThree =      _scrapeHTML(soup, datePlsThree, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_plsThree =            _scrapeHTML(soup, datePlsThree, 'UV', 'UV Index')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listStorms_plsThree =        _scrapeHTML(soup, datePlsThree, 'Significant Weather', 'Thunderstorms')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listHumid_plsThree =        _scrapeHTML(soup, datePlsThree, 'Humidity & Wind', re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly

    #DAY PLUS FOUR
    listRainMM_plsFour =        _scrapeHTML(soup, datePlsFour, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_plsFour =    _scrapeHTML(soup, datePlsFour, 'Rainfall', 'Chance of any rain')
    listTempFeel_plsFour =      _scrapeHTML(soup, datePlsFour, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_plsFour =            _scrapeHTML(soup, datePlsFour, 'UV', 'UV Index')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listStorms_plsFour =        _scrapeHTML(soup, datePlsFour, 'Significant Weather', 'Thunderstorms')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listHumid_plsFour =        _scrapeHTML(soup, datePlsFour, 'Humidity & Wind', re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly

    #DAY PLUS FIVE
    listRainMM_plsFive =        _scrapeHTML(soup, datePlsFive, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_plsFive =    _scrapeHTML(soup, datePlsFive, 'Rainfall', 'Chance of any rain')
    listTempFeel_plsFive =      _scrapeHTML(soup, datePlsFive, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_plsFive =            _scrapeHTML(soup, datePlsFive, 'UV', 'UV Index')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listStorms_plsFive =        _scrapeHTML(soup, datePlsFive, 'Significant Weather', 'Thunderstorms')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listHumid_plsFive =        _scrapeHTML(soup, datePlsFive, 'Humidity & Wind', re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly

    #DAY PLUS SIX
    listRainMM_plsSix =        _scrapeHTML(soup, datePlsSix, 'Rainfall', '50% chance of more than (mm)')
    listRainChance_plsSix =    _scrapeHTML(soup, datePlsSix, 'Rainfall', 'Chance of any rain')
    listTempFeel_plsSix =      _scrapeHTML(soup, datePlsSix, 'Temperatures', re.compile('^Feels like'))             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listUV_plsSix =            _scrapeHTML(soup, datePlsSix, 'UV', 'UV Index')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listStorms_plsSix =        _scrapeHTML(soup, datePlsSix, 'Significant Weather', 'Thunderstorms')             #regex needed as the specal chars 'Feels like (&deg;C)' throw a wobbly
    listHumid_plsSix =        _scrapeHTML(soup, datePlsSix, 'Humidity & Wind', re.compile('^Relative humidity'))   #regex needed as the specal chars 'Relative humidity (%)' throw a wobbly


    #TODAY
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = dateToday + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = dateToday + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaaTime":       stdTime}                      #aaa so it sorts first, important for splunk making this the timestamp
        mydict.update   ( {"h3rainMM":        listRainMM_tdy[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_tdy[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_tdy[i]} )
        mydict.update   ( {"h3uv":            listUV_tdy[i]} )
        mydict.update   ( {"h3storms":        listStorms_tdy[i]} )
        mydict.update   ( {"h3humid":         listHumid_tdy[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)                                        #this may look stupid to do here each iteraton, but it helps splunk ingest as seperate timestamps, otherwse it just takes the first.
        hr = hr + 3
        i = i + 1

    #TOMORROW
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = dateTmr + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = dateTmr + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaatime":       stdTime}
        mydict.update   ( {"h3rainMM":        listRainMM_tmr[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_tmr[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_tmr[i]} )
        mydict.update   ( {"h3uv":            listUV_tmr[i]} )
        mydict.update   ( {"h3storms":        listStorms_tmr[i]} )
        mydict.update   ( {"h3humid":         listHumid_tmr[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)
        hr = hr + 3
        i = i + 1

    #DAY AFTER TOMORROW
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = datePlsTwo + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = datePlsTwo + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaatime":       stdTime}
        mydict.update   ( {"h3rainMM":        listRainMM_plsTwo[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_plsTwo[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_plsTwo[i]} )
        mydict.update   ( {"h3uv":            listUV_plsTwo[i]} )
        mydict.update   ( {"h3storms":        listStorms_plsTwo[i]} )
        mydict.update   ( {"h3humid":         listHumid_plsTwo[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)
        hr = hr + 3
        i = i + 1

    #DAY PLUS THREE
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = datePlsThree + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = datePlsThree + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaatime":       stdTime}
        mydict.update   ( {"h3rainMM":        listRainMM_plsThree[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_plsThree[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_plsThree[i]} )
        mydict.update   ( {"h3uv":            listUV_plsThree[i]} )
        mydict.update   ( {"h3storms":        listStorms_plsThree[i]} )
        mydict.update   ( {"h3humid":         listHumid_plsThree[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)
        hr = hr + 3
        i = i + 1

    #DAY PLUS FOUR
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = datePlsFour + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = datePlsFour + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaatime":       stdTime}
        mydict.update   ( {"h3rainMM":        listRainMM_plsFour[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_plsFour[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_plsFour[i]} )
        mydict.update   ( {"h3uv":            listUV_plsFour[i]} )
        mydict.update   ( {"h3storms":        listStorms_plsFour[i]} )
        mydict.update   ( {"h3humid":         listHumid_plsFour[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)
        hr = hr + 3
        i = i + 1

    #DAY PLUS FIVE
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = datePlsFive + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = datePlsFive + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaatime":       stdTime}
        mydict.update   ( {"h3rainMM":        listRainMM_plsFive[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_plsFive[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_plsFive[i]} )
        mydict.update   ( {"h3uv":            listUV_plsFive[i]} )
        mydict.update   ( {"h3storms":        listStorms_plsFive[i]} )
        mydict.update   ( {"h3humid":         listHumid_plsFive[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)
        hr = hr + 3
        i = i + 1

    #DAY PLUS SIX
    i = 0
    hr = 2
    while i < 8:
        if hr < 10:
            stdTime = datePlsSix + "T0" + str(hr) + ":00:00+11:00"             #  2019-01-13T17:00:00+11:00
        else:
            stdTime = datePlsSix + "T"  + str(hr) + ":00:00+11:00"
        mydict =          {"h3aaatime":       stdTime}
        mydict.update   ( {"h3rainMM":        listRainMM_plsSix[i]} )
        mydict.update   ( {"h3rainChance":    listRainChance_plsSix[i]} )
        mydict.update   ( {"h3tempFeel":      listTempFeel_plsSix[i]} )
        mydict.update   ( {"h3uv":            listUV_plsSix[i]} )
        mydict.update   ( {"h3storms":        listStorms_plsSix[i]} )
        mydict.update   ( {"h3humid":         listHumid_plsSix[i]} )
        mydict.update   ( {"h3apiPollTime":   myProgStartTime } )
        _spitJSONoutToSplunk(mydict)
        hr = hr + 3
        i = i + 1

    resultsDict = {"BOMxmlDlTime": time.time() - myBOMStartTime}
    resultsDict.update( {"kCryptoDictType": 'BOM3hrpredictions'} )

#    _extractDayPrediction(tree,0,myBOMStartTime)

    myDict.update(resultsDict)
    return myDict

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _scrapeHTML(soup, argDate, argCat, argRow):
    argDatePrependD = "d" + argDate
    div = soup.find('div', {'id': argDatePrependD})
    heading = div.find('h3', text=argCat)
    if argRow == 'Wind speed':
        tb = heading.findNext('tbody')
    else:
        th = heading.findNext('th', text=argRow)
    td0200 = th.findNext('td')
    td0500 = td0200.findNext('td')
    td0800 = td0500.findNext('td')
    td1100 = td0800.findNext('td')
    td1400 = td1100.findNext('td')
    td1700 = td1400.findNext('td')
    td2000 = td1700.findNext('td')
    td2300 = td2000.findNext('td')

    resultsList = [td0200.text, td0500.text, td0800.text, td1100.text, td1400.text, td1700.text, td2000.text, td2300.text]
    return resultsList


#---------------------------------------------------------------------------------------------------------------------------------------------------
def _spitJSONoutToSplunk(myDict):
    print (json.dumps(myDict, indent=4, sort_keys=True))


#MAIN CODE INVOKE POINT
_main()



#---------------------------------------------------------------------------------------------------------------------------------------------------
# EXAMPLE HTML - TAKEN ON 2019-01-13  (FIXED UP INDENTENTING)
#---------------------------------------------------------------------------------------------------------------------------------------------------
'''
<h1>Sydney Detailed Forecast <span class="beta">(beta)</span></h1>
<a class="meteye-link" href="/australia/meteye/?lat=-33.85&amp;lon=151.22&amp;url=/nsw/sydney/&amp;name=Sydney">Map View <span>MetEye</span></a>
<div id="content" class="detailed">
<div id="main-content">
<p class="warning"><a href="/nsw/warnings/">View the current warnings for New South Wales</a></p>
<form action="/places/search/" id="locationSearch">
	<label for="location-search-box">Change location <span class="noshow"> Start typing (town, city, postcode or lat/lon), then select from list below.</span></label>
	<input type="text" size="24" autocomplete="off" id="location-search-box" name="q" placeholder="Start typing, then select from list (town, city, postcode or lat/lon)"/>
	<input class="submit" type="submit" value="Locate" />
	<!-- <button>Find Me</button> -->
</form>
	<div class="forecast-day collapsible" id="d2019-01-13">
		<h2 class="pointer">Sunday 13 January</h2>
		<h3>Rainfall</h3>
		<table summary="3 Hourly Rainfall Forecast for Sunday">
			<thead>
				<tr><th class="first">From</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
                    <th class="first">50% chance of more than (mm)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <th class="first">25% chance of more than (mm)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <th class="first">10% chance of more than (mm)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <th class="first">Chance of any rain</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>5%</td>
                    <td>0%</td>
                    <td>5%</td>
                    <td>5%</td>
                    <td>0%</td>
                </tr>
			</tbody>
		</table>

		<h3>Temperatures</h3>
		<table summary="3 Hourly Temperatures Forecast for Sunday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
                    <th class="first">Air temperature (&deg;C)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>26</td>
                    <td>27</td>
                    <td>26</td>
                    <td>23</td>
                    <td>22</td>
                </tr>
                <tr>
                    <th class="first">Feels like (&deg;C)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>24</td>
                    <td>26</td>
                    <td>26</td>
                    <td>25</td>
                    <td>25</td>
                </tr>
                <tr>
                    <th class="first">Dew point temperature (&deg;C)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>19</td>
                    <td>19</td>
                    <td>20</td>
                    <td>20</td>
                    <td>21</td>
                </tr>
			</tbody>
		</table>

		<h3>UV</h3>
		<table summary="3 Hourly UV Index Forecast for Sunday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
                    <th class="first">UV Index</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>10</td>
                    <td>12</td>
                    <td>3</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
			</tbody>
		</table>

		<h3>Significant Weather</h3>
		<table summary="3 Hourly Significant Weather Forecast for Sunday">
			<thead>
				<tr><th class="first">From</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <!-- TODO: run policy on these rows to add a class and change the text -->
                <tr><th class="first">Thunderstorms</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Snow</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Rain</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Fog</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Frost</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr>			</tbody>
		</table>

		<h3>Humidity &amp; Wind</h3>
		<table summary="3 Hourly Humidity &amp;amp; Wind Forecast for Sunday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr><th class="first">Wind speed  <abbr title="kilometres per hour">km/h</abbr><br /><span class="knots">knots</span></th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td data-kmh="30" data-kts="16">30<br /><span class="knots">16</span></td><td data-kmh="26" data-kts="14">26<br /><span class="knots">14</span></td><td data-kmh="20" data-kts="11">20<br /><span class="knots">11</span></td><td data-kmh="15" data-kts="8">15<br /><span class="knots">8</span></td><td data-kmh="7" data-kts="4">7<br /><span class="knots">4</span></td></tr><tr><th class="first">Wind direction</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="wind_dir S">S</td><td class="wind_dir S">S</td><td class="wind_dir SSE">SSE</td><td class="wind_dir SSE">SSE</td><td class="wind_dir SSE">SSE</td></tr><tr>
                    <th class="first">Relative humidity (%)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>66</td>
                    <td>61</td>
                    <td>68</td>
                    <td>84</td>
                    <td>92</td>
                </tr>
                <tr>
                    <th class="first">Forest fuel dryness factor</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>7.9</td>
                    <td>7.9</td>
                    <td>7.9</td>
                    <td>7.9</td>
                    <td>7.9</td>
                </tr>
                <tr>
                    <th class="first">Mixing height (m)</th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>1075</td>
                    <td>1159</td>
                    <td>1093</td>
                    <td>827</td>
                    <td>626</td>
                </tr>
			</tbody>
		</table>
    </div>

	<div class="forecast-day collapsible" id="d2019-01-14">
		<h2 class="pointer">Monday 14 January</h2>
		<h3>Rainfall</h3>
		<table summary="3 Hourly Rainfall Forecast for Monday">
			<thead>
				<tr><th class="first">From</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
                    <th class="first">50% chance of more than (mm)</th>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <th class="first">25% chance of more than (mm)</th>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <th class="first">10% chance of more than (mm)</th>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
                <tr>
                    <th class="first">Chance of any rain</th>
                    <td>0%</td>
                    <td>0%</td>
                    <td>5%</td>
                    <td>0%</td>
                    <td>0%</td>
                    <td>0%</td>
                    <td>0%</td>
                    <td>0%</td>
                </tr>
			</tbody>
		</table>

		<h3>Temperatures</h3>
		<table summary="3 Hourly Temperatures Forecast for Monday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
                    <th class="first">Air temperature (&deg;C)</th>
                    <td>21</td>
                    <td>22</td>
                    <td>24</td>
                    <td>29</td>
                    <td>29</td>
                    <td>28</td>
                    <td>25</td>
                    <td>24</td>
                </tr>
                <tr>
                    <th class="first">Feels like (&deg;C)</th>
                    <td>25</td>
                    <td>25</td>
                    <td>27</td>
                    <td>29</td>
                    <td>28</td>
                    <td>26</td>
                    <td>24</td>
                    <td>24</td>
                </tr>
                <tr>
                    <th class="first">Dew point temperature (&deg;C)</th>
                    <td>21</td>
                    <td>21</td>
                    <td>21</td>
                    <td>19</td>
                    <td>19</td>
                    <td>20</td>
                    <td>20</td>
                    <td>19</td>
                </tr>
			</tbody>
		</table>

		<h3>UV</h3>
		<table summary="3 Hourly UV Index Forecast for Monday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
                    <th class="first">UV Index</th>
                    <td>0</td>
                    <td>0</td>
                    <td>1</td>
                    <td>10</td>
                    <td>12</td>
                    <td>3</td>
                    <td>0</td>
                    <td>0</td>
                </tr>
			</tbody>
		</table>

		<h3>Significant Weather</h3>
		<table summary="3 Hourly Significant Weather Forecast for Monday">
			<thead>
				<tr><th class="first">From</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <!-- TODO: run policy on these rows to add a class and change the text -->
                <tr><th class="first">Thunderstorms</th><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Snow</th><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Rain</th><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Fog</th><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr><tr><th class="first">Frost</th><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td><td class="False">No</td></tr>			</tbody>
		</table>

		<h3>Humidity &amp; Wind</h3>
		<table summary="3 Hourly Humidity &amp;amp; Wind Forecast for Monday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr><th class="first">Wind speed  <abbr title="kilometres per hour">km/h</abbr><br /><span class="knots">knots</span></th><td data-kmh="4" data-kts="2">4<br /><span class="knots">2</span></td><td data-kmh="4" data-kts="2">4<br /><span class="knots">2</span></td><td data-kmh="6" data-kts="3">6<br /><span class="knots">3</span></td><td data-kmh="15" data-kts="8">15<br /><span class="knots">8</span></td><td data-kmh="20" data-kts="11">20<br /><span class="knots">11</span></td><td data-kmh="28" data-kts="15">28<br /><span class="knots">15</span></td><td data-kmh="31" data-kts="17">31<br /><span class="knots">17</span></td><td data-kmh="22" data-kts="12">22<br /><span class="knots">12</span></td></tr><tr><th class="first">Wind direction</th><td class="wind_dir SSE">SSE</td><td class="wind_dir ESE">ESE</td><td class="wind_dir NE">NE</td><td class="wind_dir NE">NE</td><td class="wind_dir NE">NE</td><td class="wind_dir NE">NE</td><td class="wind_dir NE">NE</td><td class="wind_dir NNE">NNE</td></tr><tr>
                    <th class="first">Relative humidity (%)</th>
                    <td>98</td>
                    <td>92</td>
                    <td>82</td>
                    <td>57</td>
                    <td>58</td>
                    <td>61</td>
                    <td>74</td>
                    <td>75</td>
                </tr>
                <tr>
                    <th class="first">Forest fuel dryness factor</th>
                    <td>7.9</td>
                    <td>7.9</td>
                    <td>7.9</td>
                    <td>8</td>
                    <td>8</td>
                    <td>8</td>
                    <td>8</td>
                    <td>8</td>
                </tr>
                <tr>
                    <th class="first">Mixing height (m)</th>
                    <td>416</td>
                    <td>649</td>
                    <td>935</td>
                    <td>1197</td>
                    <td>1010</td>
                    <td>791</td>
                    <td>229</td>
                    <td>21</td>
                </tr>
			</tbody>
		</table>
    </div>

	<div class="forecast-day collapsible" id="d2019-01-15">
		<h2 class="pointer">Tuesday 15 January</h2>


    <h3>Humidity &amp; Wind</h3>
	<table summary="3 Hourly Humidity &amp;amp; Wind Forecast for Sunday">
			<thead>
				<tr><th class="first">At</th>
					<th>2:00 AM</th><th>5:00 AM</th><th>8:00 AM</th><th>11:00 AM</th><th>2:00 PM</th><th>5:00 PM</th><th>8:00 PM</th><th>11:00 PM</th>				</tr>
			</thead>
			<tbody>
                <tr>
***THIS NEXT LINE IS SCREWED, MESSES UP THE PARSING, I GUESS CAUSE DOUBLE OPEN....***
                    <th class="first">Wind speed  <abbr title="kilometres per hour">km/h</abbr><br /><span class="knots">knots</span></th>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td>&ndash;</td>
                    <td data-kmh="30" data-kts="16">30<br /><span class="knots">16</span></td>
                    <td data-kmh="26" data-kts="14">26<br /><span class="knots">14</span></td>
                    <td data-kmh="20" data-kts="11">20<br /><span class="knots">11</span></td>
                    <td data-kmh="15" data-kts="8">15<br /><span class="knots">8</span>
                    </td><td data-kmh="7" data-kts="4">7<br /><span class="knots">4</span>
                    </td>
                </tr>
                <tr><th class="first">Wind direction</th><td>&ndash;</td><td>&ndash;</td><td>&ndash;</td><td class="wind_dir S">S</td><td class="wind_dir S">S</td><td class="wind_dir SSE">SSE</td><td class="wind_dir SSE">SSE</td><td class="wind_dir SSE">SSE</td></tr><tr>


{}


        '''
