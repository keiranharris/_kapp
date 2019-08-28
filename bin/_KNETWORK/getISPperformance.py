########################################
# VERSION:  GIT'ified
# UPDATED:  GIT'ified
# DESCRIP:  scripted inputs for bex36 splunk ISP data - now JSON format
# NOTES:
########################################


import sys 				#for sys.stdout.write(plusCurlList)
import datetime  		#to convert epoch to human readable
import urllib, json
import time  			#TO MEASURE EXECUTION TIMES
import socket			#FOR DNS OPERATIONS
from subprocess import Popen, PIPE
#from pythonping import ping     #for ping


#GLOBAL VARIABLES
myProgStartTime = time.time()

#TO AVOID RANDOM ISSUES ('Popen; errread, errwrite; no such file or directory' - only when splunk's version of python invokes, system python is ok!)  - USE THE FULL PATH (use 'which' to locate on HDD)
IPERF_EXECUTABLE        = "/usr/local/bin/iperf3"
CURL_EXECUTABLE         = "/usr/bin/curl"
SPEEDTEST_EXECUTABLE    = "/usr/local/bin/speedtest-cli"

def _main():
    scriptStartTime = time.time()

    myDict 	        = {}
    myDict 	        = _collectDNSdata(myDict)
#    myDict 	        = _collectPINGdata(myDict)                 ............pythonping only supports python v3 so diable until then
    myDict          = _collectCURLdata(myDict, CURL_EXECUTABLE)
<<<<<<< HEAD
    #COMMENTED OUT AUG2019 AS IT WAS ALWAYS 'SERVER BUSY' AND TAKING AGES TO RETURN (>180secs)
    #myDict          = _collectIPERFdata(myDict, IPERF_EXECUTABLE)
=======
#    myDict          = _collectIPERFdata(myDict, IPERF_EXECUTABLE)
>>>>>>> 3a3a891295fceafe0c69609859405a582c915243
    myDict          = _collectSPEEDTESTdata(myDict, SPEEDTEST_EXECUTABLE)
    _spitJSONoutToSplunk(myDict)
    #_logToFile()

    scriptRunTime = {"ScriptRunTime_GETISPPERFORMANCE.py":  time.time() - scriptStartTime}
    _spitJSONoutToSplunk(scriptRunTime)



def _logToFile():
	f = open('/_LOCALDATA/_PROGDATA/SCRIPTS/_LOGS/ksplunkscriptedinput.log', 'a')
	f.write('hi there myProgStartTime: ' + str(datetime.datetime.fromtimestamp(myProgStartTime).strftime('%c')) + '\n')  # python will convert \n to os.linesep
	f.close()  # you can omit in most cases as the destructor will call it


def _collectDNSdata(myDict):
    myDNSStartTime = time.time()
    addr1 = socket.gethostbyname('bluegum.com')
#	myList.append("DNSqryTime=" + str(time.time() - myDNSStartTime))
    resultsDict = {"DNSqryTime": time.time() - myDNSStartTime}
    myDict.update(resultsDict)
    return myDict

def _collectPINGdata(myDict):
    response_list = ping('8.8.8.8')
    print (response_list.rtt_avg_ms)
    #resultsDict = {"PINGtime": response_list.rtt_avg_ms}
    myDict.update(resultsDict)
    return myDict

def _collectCURLdata(myDict, executable):
    args = list()
    args.append("http://bluegum.com/")
    args.append("-o /dev/null")		#direct html output to bit bucket
    args.append("-s")				#silent
    args.append("-w %{time_namelookup}:%{time_connect}:%{time_starttransfer}:%{time_total}")
    curl_command = [executable] + args

    #EXECUTE THE BASH-LEVEL COMMAND, STORING STDIN/STDOUT/STDERR
    p = Popen(curl_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (output, err) = p.communicate(b"input data that is passed to subprocess' stdin")
    rc = p.returncode

    #SPLIT THE LIST
    mySplitList = output.split(":")
#	myList.append("CURLdnsTime=%s"		% str(mySplitList[0]).lstrip())
    resultsDict = {"CURLdnsTime":          float(str(mySplitList[0]).lstrip())}
    resultsDict.update({"CURLconnectTime": float(str(mySplitList[1]))})
    resultsDict.update({"CURLstartXfer":   float(str(mySplitList[2]))})
    resultsDict.update({"CURLtotalTime":   float(str(mySplitList[3]))})
    myDict.update(resultsDict)
    return myDict


def _collectIPERFdata(myDict, executable):
	#NOTE: this function requires "developer tools" to be installed (type from from cli: 'xcode-select --install' - requires GUI)
	#	then you miust install iperf3 via brew (type from cli: 'brew install iperf3')
	#UPLOAD DIRECTION-----------------------------------------------------
        args = list()
        args.append("-c")				#client side (data push client -> server)
        args.append("iperf.he.net")		#public iperf server
        args.append("-t 5")				#run for t secs
        args.append("-O 2")				#ommiting first O secs (avoids tcp slowstart)
        args.append("-J")				#return results in JSON format
        iperf_command = [executable] + args

        #EXECUTE THE BASH-LEVEL COMMAND, STORING STDIN/STDOUT/STDERR.... note 'command' must be a LIST, the first element being the exe, and subsequent being CLI arguments. If you dont like this format use 'shell=True' then you can pass a dumbed down string will all arguments embedded.
        p = Popen(iperf_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        (output, err) = p.communicate(b"input data that is passed to subprocess' stdin")
        rc = p.returncode
        #IF YOU NEED TO SEE THE JSON UNCOMMENT THIS
        #print output

        #LOAD THE OUTPUT OF ABOVE INTO JSON PARSER
        data = json.loads(output)

        #CHECK FOR SERVER BUSY ERROR: "error - the server is busy running a test. try again later"
        if 'error' in data:
            resultsDict = {"IPERFupMbps": "SVR-BUSY"}
        else:
            up = data['end']['streams'][0]['sender']['bits_per_second']
            resultsDict = {"IPERFupMbps": float(str(up))}

    #DOWNLOAD DIRECTION--------------------------------------------------
        args.append("-R")			#run in reverse direction (remote server -> client)
        iperf_command = [executable] + args

        #EXECUTE THE BASH-LEVEL COMMAND, STORING STDIN/STDOUT/STDERR.... note 'command' must be a LIST, the first element being the exe, and subsequent being CLI arguments. If you dont like this format use 'shell=True' then you can pass a dumbed down string will all arguments embedded.
        p = Popen(iperf_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        (output, err) = p.communicate(b"input data that is passed to subprocess' stdin")
        rc = p.returncode

        #LOAD THE OUTPUT OF ABOVE INTO JSON PARSER
        data = json.loads(output)

        #CHECK FOR SERVER BUSY ERROR: "error - the server is busy running a test. try again later"
        if 'error' in data:
            resultsDict.update({"IPERFdownMbps": "SVR-BUSY"})
        else:
            down = data['end']['streams'][0]['receiver']['bits_per_second']
            resultsDict.update({"IPERFdownMbps": float(str(down))})

        myDict.update(resultsDict)
        return myDict


def _collectSPEEDTESTdata(myDict, executable):
    args = list()
    args.append("--json")				#spit out in JSON format
    speedtest_command = [executable] + args

    #EXECUTE THE BASH-LEVEL COMMAND, STORING STDIN/STDOUT/STDERR.... note 'command' must be a LIST, the first element being the exe, and subsequent being CLI arguments. If you dont like this format use 'shell=True' then you can pass a dumbed down string will all arguments embedded.
    p = Popen(speedtest_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (output, err) = p.communicate(b"input data that is passed to subprocess' stdin")
    rc = p.returncode

    #LOAD THE OUTPUT OF ABOVE INTO JSON PARSER
    data = json.loads(output)
    down = data['download']
    up   = data['upload']

    resultsDict =       {"SPEEDTESTdownMbps":   float(str(down))}
    resultsDict.update( {"SPEEDTESTupMbps":     float(str(up))})

    myDict.update(resultsDict)
    return myDict

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _spitJSONoutToSplunk(myDict):
    print (json.dumps(myDict, indent=4, sort_keys=True))

#MAIN CODE INVOKE POINT
_main()
