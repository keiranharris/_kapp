########################################
# VERSION:  GIT'ified
# UPDATED:  GIT'ified
# DESCRIP:  scripted inputs for bex36 splunk ISP data - now JSON format
# NOTES:    requires:
#                'pip install pysnmp'.... then copy these library files over
#                     - ***note OSX python is diff to splunk python!!!***  so pip above will pump to wrong location, fix is to manually copy all new (sort by date) files/directories from the pip install ie.  /Library/Python/2.7/site-packages/ --->  /Applications/Splunk/lib/python2.7/site-packages/

########################################


from pysnmp import hlapi
import time  			#TO MEASURE EXECUTION TIMES
import json
import os               #TO WORK AROUND LACK OF UPDATE PROBLEM

PFSENSEIP = '10.1.5.1'

''' EXAMPLE JSON OUTPUT
{
    "MemInUse": 36879,
    "ScriptRunTime_GETPFSENSESTATS.py": 0.25839996337890625,
    "kNetworkDictType": "pfsense",
    "searchesAgainstState": 571312576,
    "stateTableSessions": 707,
    "vCPU1load": 0,
    "vCPU2load": 0,
    "vtnet0BytesInDeny": 844529,
    "vtnet0BytesInPass": 181283352077,
    "vtnet0BytesOutDeny": 1360,
    "vtnet0BytesOutPass": 22475090420,
    "vtnet0ppsIn": 164209342,
    "vtnet0ppsOut": 117603229
}
'''

def _main():
    scriptStartTime = time.time()

    oidList = []
    oidList.append('1.3.6.1.2.1.25.2.3.1.6.1')                    #memory in use
    oidList.append('1.3.6.1.2.1.25.3.3.1.2.75')                   #vCPU-1 load
    oidList.append('1.3.6.1.2.1.25.3.3.1.2.76')                   #vCPU-2 load
    oidList.append('1.3.6.1.4.1.12325.1.200.1.3.1.0')             #state table (session count)
    oidList.append('1.3.6.1.4.1.12325.1.200.1.3.2.0')             #searhes against state table
    oidList.append('1.3.6.1.4.1.12325.1.200.1.8.2.1.7.10')        #Bytes in PASS (vtnet0)
    oidList.append('1.3.6.1.4.1.12325.1.200.1.8.2.1.8.10')        #Bytes in DENY (vtnet0)
    oidList.append('1.3.6.1.4.1.12325.1.200.1.8.2.1.9.10')        #Bytes out PASS (vtnet0)
    oidList.append('1.3.6.1.4.1.12325.1.200.1.8.2.1.10.10')       #Bytes out DENY (vtnet0)
    oidList.append('1.3.6.1.4.1.12325.1.200.1.8.2.1.11.10')       #PPS in (vtnet0)
    oidList.append('1.3.6.1.4.1.12325.1.200.1.8.2.1.13.10')       #PPS out (vtnet0)

    #FORCE AN UPDATE OF THE STALE SNMP COUNTERS
    myCmd = 'snmpget -c s3cur3d 10.1.5.1    1.3.6.1.4.1.12325.1.200.1.8.2.1.7.10   > /dev/null'
    os.system(myCmd)

    snmpDict = _snmpPoke(PFSENSEIP, oidList, hlapi.CommunityData('s3cur3d'))
    #_spitJSONoutToSplunk(hello)

    myDict = {"kNetworkDictType": 'pfsense'}

    for kOid, kValue in snmpDict.items():
        #print(kOid, ":", kOid)
        #SYSTEM LEVEL COUNTERS
        if kOid == '1.3.6.1.2.1.25.2.3.1.6.1':
            myDict.update(    {"MemInUse":    kValue} )
        if kOid == '1.3.6.1.2.1.25.3.3.1.2.75':
            myDict.update(    {"vCPU1load":    kValue} )
        if kOid == '1.3.6.1.2.1.25.3.3.1.2.76':
            myDict.update(    {"vCPU2load":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.3.1.0':
            myDict.update(    {"stateTableSessions":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.3.2.0':
            myDict.update(    {"searchesAgainstState":    kValue} )
        #VTNET0 (WAN) COUNTERS
        if kOid == '1.3.6.1.4.1.12325.1.200.1.8.2.1.7.10':
            myDict.update(    {"vtnet0BytesInPass":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.8.2.1.8.10':
            myDict.update(    {"vtnet0BytesInDeny":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.8.2.1.9.10':
            myDict.update(    {"vtnet0BytesOutPass":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.8.2.1.10.10':
            myDict.update(    {"vtnet0BytesOutDeny":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.8.2.1.11.10':
            myDict.update(    {"vtnet0ppsIn":    kValue} )
        if kOid == '1.3.6.1.4.1.12325.1.200.1.8.2.1.13.10':
            myDict.update(    {"vtnet0ppsOut":    kValue} )

    myDict.update(    {"ScriptRunTime_GETPFSENSESTATS.py":  time.time() - scriptStartTime} )
    _spitJSONoutToSplunk(myDict)


#---------------------------------------------------------------------------------------------------------------------------------------------------
def _snmpPoke(target, oids, credentials, port=161, engine=hlapi.SnmpEngine(), context=hlapi.ContextData()):
    handler = hlapi.getCmd( engine, credentials, hlapi.UdpTransportTarget((target, port)), context, *construct_object_types(oids) )
    return fetch(handler, 1)[0]

def construct_object_types(list_of_oids):
    object_types = []
    for oid in list_of_oids:
        object_types.append(hlapi.ObjectType(hlapi.ObjectIdentity(oid)))
    return object_types

def fetch(handler, count):
    result = []
    for i in range(count):
        try:
            error_indication, error_status, error_index, var_binds = next(handler)
            if not error_indication and not error_status:
                items = {}
                for var_bind in var_binds:
                    items[str(var_bind[0])] = cast(var_bind[1])
                result.append(items)
            else:
                raise RuntimeError('Got SNMP error: {0}'.format(error_indication))
        except StopIteration:
            break
    return result

def cast(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        try:
            return float(value)
        except (ValueError, TypeError):
            try:
                return str(value)
            except (ValueError, TypeError):
                pass
    return value

#---------------------------------------------------------------------------------------------------------------------------------------------------
def _spitJSONoutToSplunk(myDict):
    print (json.dumps(myDict, indent=4, sort_keys=True))

#---------------------------------------------------------------------------------------------------------------------------------------------------
#MAIN CODE INVOKE POINT
_main()
