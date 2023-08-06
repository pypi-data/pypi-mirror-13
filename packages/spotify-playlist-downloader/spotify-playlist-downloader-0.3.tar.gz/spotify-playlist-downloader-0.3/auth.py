import os
import json
import urllib
import urllib2
import re
import requests
import time

class Auth:
    def __init__(self):
        client_id = 'd56ed89f1ba04b3e89a6e3df3a99b91c'
        client_secret = 'ac839d4102a24c62b28008675161ef07'
        redirect_uri = 'http://www.google.com'
        
        auth_url = "https://accounts.spotify.com/api/token"
        auth_values = {'grant_type': 'client_credentials','scope': 'user-read-private', 'client_id': client_id, 'client_secret': client_secret}
        auth_response = self.http_request_response(auth_url, auth_values, 'POST')
        

        self.access_token = auth_response['access_token']
        self.auth_dict = {'Authorization': 'Bearer ' + self.access_token}
        
    def http_request_response(self, url, values, req_type):
        if req_type == 'GET':
                request = urllib2.Request(url, headers = values)
        elif req_type == 'POST':
                data = urllib.urlencode(values)
                request = urllib2.Request(url, data)

        response = json.load(urllib2.urlopen(request))

        return response


#parallel wget; remove os wget; command line application python; for pandora too; get spotify playlist data without api
