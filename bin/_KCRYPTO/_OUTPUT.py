import json             #FOR JSON OPERATIONS
import requests         #FOR SLACK API POST.... note, this requires:   'pip install --upgrade requests'  (dont forget to then manually copy stuff from /Library/Python/2.7/site-packages --->  /Applications/Splunk/lib/python2.7/site-packages



#---------------------------------------------------------------------------------------------------------------------------------------------------
# OUTPUT FUNCTIONS
#---------------------------------------------------------------------------------------------------------------------------------------------------

def _spitJSONoutToSplunk(myDict):
    print (json.dumps(myDict, indent=4, sort_keys=True))

def _pushMessageToSlack(webhook_url, slack_post):  # lowOrHigh, coin, current, threshold):
    #NOTE: enanale a new webhooks API here:   https://my.slack.com/services/new/incoming-webhook/
    slack_post = {'text': slack_post}
    response = requests.post( webhook_url, data=json.dumps(slack_post), headers={'Content-Type': 'application/json'} )
    if response.status_code != 200:
        raise ValueError(
            'Request to slack returned an error %s, the response is:\n%s'
            % (response.status_code, response.text)
        )
    return

def _logToFile():
    f = open('/_LOCALDATA/_PROGDATA/SCRIPTS/_LOGS/ksplunkscriptedinput.log', 'a')
    f.write('hi there myProgStartTime: ' + str(datetime.datetime.fromtimestamp(myProgStartTime).strftime('%c')) + '\n')  # python will convert \n to os.linesep
    f.close()  # you can omit in most cases as the destructor will call it
