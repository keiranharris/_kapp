################################################################################################### GOOGLE SHEETS API K NOTES
#K-NOTES: lots of moving parts here!
# REF: https://developers.google.com/sheets/api/quickstart/python   and    https://developers.google.com/sheets/api/guides/values
#  0/ pre-req's:
#       A- need to have installed pip (sudo easy_install pip)... wbich is the python package manager (to pull down new libraries)
#       B- then need the google libraries ( pip install --upgrade google-api-python-client )
#       C- you might get this error when doing so ("DEPRECATION: Uninstalling a distutils installed project (six) has been deprecated...."), if so, you can add ' --upgrade --ignore-installed six ' to the end of the above command.   SEE https://github.com/donnemartin/haxor-news/issues/54
#       D- ***note OSX python is diff to splunk python!!!***  so pip above will pump to wrong location, fix is to manually copy all new (sort by date) files/directories from the pip install ie.  /Library/Python/2.7/site-packages/ --->  /Applications/Splunk/lib/python2.7/site-packages/
#       E- then you will need to run this code (getCrypto.py) from THAT splunk instance /Applications/Splunk/bin/python getCrypto.py --noauth_local_webserver   ... beware if you are running as TV or ROOT! (should be ROOT, as splunk runs as root... [port issue])
#  1/ theres a local JSON file 'getCrypto_gsheetsClientSecret.json' that needs to be linked when you first run it (see global variables). This file came from tutorial here: https://developers.google.com/sheets/api/quickstart/python
#  2/ first time you run this python code, you need to supply an additional CLI arg ( --noauth_local_webserver ) to force it through non-interactive CLI based auth
#  3/ this, when successul, places a credentials file in ~/.credentials/sheets.googleapis.com-python-quickstart.json on your LOCAL MACHINE (not in g-cloud)... anytime you wish to retrigger new auth, delete this file
################################################################################################### GOOGLE SHEETS API HEADER CODE
from __future__ import print_function   #GOOGLE SHEETS REQUIRES THIS AT THE START
import httplib2
import os
import apiclient
#from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

#GLOBAL VARIABLES
SCOPES = 'https://www.googleapis.com/auth/spreadsheets'                                     #<<< 'https://www.googleapis.com/auth/spreadsheets.readonly'  <<<KNOTE ALSO A READONLY VERSION
CLIENT_SECRET_FILE = '/_LOCALDATA/_PROGDATA/SCRIPTS/getCrypto_gsheetsClientSecret.json'     #<<< SEE K-NOTES ABOVE.
APPLICATION_NAME = 'GSheets-API'                                                            #<<< APP NAME SET WHEN YOU TURN ON THE API IN GOOGLE CLOUD.
spreadsheetId = '1oZd3rPcxL3rWq1_-rd7vI3RI35hf4RIxyUsQ6f8kau8'                              #spreadsheetId - GET FROM THE MIDDLE PART OF THE G-SHEET URL https://docs.google.com/spreadsheets/d/1oZd3rPcxL3rWq1_-rd7vI3RI35hf4RIxyUsQ6f8kau8/edit#gid=1173760650
######################################################################################################


#---------------------------------------------------------------------------------------------------------------------------------------------------
# GOOGLE SHEETS FUNCTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------
def getGoogleCredentials():
    #Gets valid user credentials from storage. If nothing has been stored, or if the stored credentials are invalid, the OAuth2 flow is completed to obtain the new credentials. Returns: Credentials, the obtained credential.
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir, 'sheets.googleapis.com-python-quickstart.json')
    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def _readFromGoogleSheet(rangeName):
    # DESCR:    given a gSheet range, return a list of lists with the data.
    # UPDATES:  nothing
    # RETURNS:  list of lists (each list being a row from the sheet) ie:
    #   [
    #       [u'BTC', u'21600.00', u'16600.00', u'23000.00', u'onAlert', u'onAlert', u'38.6%', u'0.000', u'0.000', u'$0.00', u'0%', u'', u'0.0400864', u'0.0000000', u'$865.87', u'1%'],
    #       [u'ETH', u'1368.97', u'950.00', u'1300.00', u'onAlert', u'FIRED', u'36.8%', u'32.762', u'3.988', u'$50,309.84', u'64%', u'', u'0.0000000', u'0.0000000', u'$0.00', u'0%'],
    #   ]
    credentials = getGoogleCredentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    result = service.spreadsheets().values().get(spreadsheetId=spreadsheetId, range=rangeName).execute()
    values = result.get('values', [])
    return values

def _publishToGoogleSheet(valuesToWrite,myValueInputOption,cellRangeToWriteTo,directionToWrite):
    #NOTE: BE AWARE EACH TIME YOU CALL THIS IT TAKES ABOUT 1.6 SECONDS TO RUN.... USE SPARINGLY
    credentials = getGoogleCredentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?' 'version=v4')
    service = discovery.build('sheets', 'v4', http=http, discoveryServiceUrl=discoveryUrl)
    body = {
        'values' : valuesToWrite,
        'majorDimension' : directionToWrite,   #NEEDED WHEN YOU WISH TO WRITE VALUES VERTICALLY
    }
    result = service.spreadsheets().values().update(spreadsheetId=spreadsheetId, range=cellRangeToWriteTo, valueInputOption=myValueInputOption, body=body).execute()
