import os
import urllib
import urllib2
import re
import requests
import time

class Playlists:
    def __init__(self, username, auth_vals):
        playlists_url = "https://api.spotify.com/v1/users/" + username + "/playlists"
        playlists_values = auth_vals.auth_dict
        playlists_response = auth_vals.http_request_response(playlists_url, playlists_values, 'GET')
        self.playlist_names, self.playlist_ids, self.playlist_owners = self.get_user_playlists(playlists_response)
        
    def get_user_playlists(self, data):
        playlist_names = []
        playlist_ids = []
        playlist_owners = []
        for i in range(len(data['items'])):
                playlist_names.append(data['items'][i]['name'])
                playlist_ids.append(data['items'][i]['id'])
                playlist_owners.append(data['items'][i]['owner']['id'])
        return playlist_names, playlist_ids, playlist_owners

    def display_playlists(self):
        for i in range(len(self.playlist_names)):
                print i+1, self.playlist_names[i]

