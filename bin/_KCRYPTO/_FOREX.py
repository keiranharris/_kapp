########################################
# VERSION:  1.0
# UPDATED:  18/05/2019
# DESCRIP:  forex pull.... free (after 1forge started charging for their API - 20190516)
# NOTES:    you must 'pip install forex-python
#        note OSX python is diff to splunk python!!!***  so pip above will pump to wrong location, fix is to manually copy all new (sort by date) files/directories from the pip install ie.  /Library/Python/2.7/site-packages/ --->  /Applications/Splunk/lib/python2.7/site-packages/'
#       then you will need to run this code from THAT splunk instance /Applications/Splunk/bin/python XXXXXXXX.py --noauth_local_webserver   ... beware if you are running as TV or ROOT! (should be ROOT, as splunk runs as root... [port issue])
########################################


from forex_python.converter import CurrencyRates

def _getForex(currency1, currency2):
    c = CurrencyRates()
    forexRate = c.get_rate(currency1, currency2)
    return forexRate
