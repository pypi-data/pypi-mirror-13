"""
Jambase API Client for Django/Python Applications

Author: Eric James Foster
EMail: maniphestival@gmail.com
License: MIT
Version: 1.0.0
URL: "https://pypi.python.org/pypi/DjamBase/1.0.0"

"""

import requests



class API(object):

    api_key = ""
    format = "json"
    base_url = "http://api.jambase.com/"

    def __init__(self, key, format="json"):
        self.api_key = key
        self.format = format

    def event_list(self, params):
        url = self.base_url + "events?" + "o=%s&api_key=%s"  % (self.format, self.api_key.lower())
        r = requests.get(url, params=params)
        print "Status Code: " + str(r.status_code), "--- URL: " + r.url
        return Response(r)



    def artist_search(self, params):
        url = self.base_url + "artists?" + "o=%s&api_key=%s"  % (self.format, self.api_key.lower())
        r = requests.get(url, params=params)
        print url
        print "Status Code: " + str(r.status_code), "--- URL: " + r.url
        return Response(r)


    def venue_search(self, params):
        url = self.base_url + "venues?" + "o=%s&api_key=%s"  % (self.format, self.api_key.lower())
        r = requests.get(url, params=params)
        print "Status Code: " + str(r.status_code), "--- URL: " + r.url
        return Response(r)



class Response(object):

    def __init__(self, r):
        self.r = r
        self.body = r.json()
        self.status = r.status_code
        self.text = r.text
        self.binary = r.content
