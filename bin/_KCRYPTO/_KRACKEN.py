# This file is part of krakenex.
#
# krakenex is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# krakenex is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser
# General Public LICENSE along with krakenex. If not, see
# <http://www.gnu.org/licenses/gpl-3.0.txt>.


import httplib
import urllib

import json

# private query nonce
import time

# private query signing
import hashlib
import hmac
import base64

#from krakenex import connection


#---------------------------------------------------------------------------------------------------------------------------------------------------
# K-NOTES:  kracken API doco is here   https://www.kraken.com/help/api
#---------------------------------------------------------------------------------------------------------------------------------------------------
# K-HEADERS
import _OUTPUT
import _GOOGLE

class Connection:
    """Kraken.com connection handler.
    Public methods:
    close
    """


    def __init__(self, uri = 'api.kraken.com', timeout = 30):
        """ Create an object for reusable connections.

        Arguments:
        uri     -- URI to connect to (default: 'https://api.kraken.com')
        timeout -- blocking operations' timeout in seconds (default: 30)
        """
        self.headers = {
            'User-Agent': 'krakenex/0.0.5 (+https://github.com/veox/python2-krakenex)'
        }

        self.conn = httplib.HTTPSConnection(uri, timeout = timeout)


    def close(self):
        """ Close the connection.
        No arguments.
        """
        self.conn.close()


    def _request(self, url, req = {}, headers = {}):
        """ Send POST request to API server.

        url     -- Fully-qualified URL with all necessary urlencoded
                   information (string, no default)
        req     -- additional API request parameters (default: {})
        headers -- additional HTTPS headers, such as API-Key and API-Sign
                   (default: {})
        """
        data = urllib.urlencode(req)
        headers.update(self.headers)

        self.conn.request("POST", url, data, headers)
        response = self.conn.getresponse()

        return response.read()



class API(object):
    """Kraken.com cryptocurrency Exchange API.

    Public methods:
    load_key
    query_public
    query_private

    """
    def __init__(self, key = '', secret = ''):
        """Create an object with authentication information.

        Arguments:
        key    -- key required to make queries to the API (default: '')
        secret -- private key used to sign API messages (default: '')

        """
        self.key = key
        self.secret = secret
        self.uri = 'https://api.kraken.com'
        self.apiversion = '0'


    def load_key(self, path):
        """Load key and secret from file.

        Argument:
        path -- path to file (string, no default)

        """
        with open(path, "r") as f:
            self.key = f.readline().strip()
            self.secret = f.readline().strip()


    def _query(self, urlpath, req = {}, conn = None, headers = {}):
        """Low-level query handling.

        Arguments:
        urlpath -- API URL path sans host (string, no default)
        req     -- additional API request parameters (default: {})
        conn    -- kraken.Connection object (default: None)
        headers -- HTTPS headers (default: {})

        """
        url = self.uri + urlpath

        if conn is None:
#            conn = connection.Connection()
            conn = Connection()


        ret = conn._request(url, req, headers)
        return json.loads(ret)


    def query_public(self, method, req = {}, conn = None):
        """API queries that do not require a valid key/secret pair.

        Arguments:
        method -- API method name (string, no default)
        req    -- additional API request parameters (default: {})
        conn   -- connection object to reuse (default: None)

        """
        urlpath = '/' + self.apiversion + '/public/' + method

        return self._query(urlpath, req, conn)


    def query_private(self, method, req={}, conn = None):
        """API queries that require a valid key/secret pair.

        Arguments:
        method -- API method name (string, no default)
        req    -- additional API request parameters (default: {})
        conn   -- connection object to reuse (default: None)

        """
        urlpath = '/' + self.apiversion + '/private/' + method

        req['nonce'] = int(1000*time.time())
        postdata = urllib.urlencode(req)
        message = urlpath + hashlib.sha256(str(req['nonce']) +
                                           postdata).digest()
        signature = hmac.new(base64.b64decode(self.secret),
                             message, hashlib.sha512)
        headers = {
            'API-Key': self.key,
            'API-Sign': base64.b64encode(signature.digest())
        }

        return self._query(urlpath, req, conn, headers)



def _KRACKENapiNoAuth_getTickr(coinList):
    myKRACKENStartTime = time.time()

    x = API()
    resultsDict = {"kCryptoDictType": 'KRACKENticker'}

    for i in range(len(coinList)):
        workingCoin = coinList[i]
        #CODE TO DIVE DOWN SEVERAL LAYERS OF THE JSON DATA STRUCTURE.... SEE THE JSON AT THE TAIL END OF THIS FILE TO UNDERSTAND
        fullCoinJson = x.query_public("Ticker", {"pair": coinList[i] } )
#        print(fullCoinJson)
        resultPop = fullCoinJson.pop ('result')
        #KRACKEN JSON RETURNS STUPID INTERMINGLING OF X AND Y CHARACTERS SO 'ETHGBP' BECOMES 'XETHZGBP'... BUT NOT FOR BCH!! GARRRGHH
        if workingCoin == "BCHEUR":
            coinKrackenified = workingCoin
        else:
            coinKrackenified = "X" + workingCoin[0:3] + "Z" +  workingCoin[3:6]
        codePop = resultPop.pop (coinKrackenified)
        cPop = codePop.pop ('c')
        resultsDict.update({   workingCoin:   {"lastPrice": cPop[0], "aaCoin": workingCoin, } } )

    resultsDict.update ({"zzKRACKENTjsonDlTime":  time.time() - myKRACKENStartTime})
    return resultsDict






#---------------------------------------------------------------------------------------------------------------------------------------------------
# JSON DATA STRUCTURES
#---------------------------------------------------------------------------------------------------------------------------------------------------
'''

    KRACKEN TICKER .....
    {
        "error": [],
        "result": {
            "XETHZGBP": {               <<<<< ETH AGAINST GBP
                "a": [
                    "543.42000",
                    "1",
                    "1.000"
                ],
                "b": [
                    "527.93000",
                    "1",
                    "1.000"
                ],
                "c": [                  <<<<< 'c' = LAST TRADE PRICE
                    "543.20000",
                    "0.05468126"
                ],
                "h": [
                    "543.20000",
                    "567.90000"
                ],
                "l": [
                    "456.00000",
                    "456.00000"
                ],
                "o": "503.11000",
                "p": [
                    "507.47456",
                    "526.34896"
                ],
                "t": [
                    24,
                    100
                ],
                "v": [
                    "1.79047575",
                    "17.60353654"
                ]
            }
        }
    }
'''
