import os
import urllib
import urllib2
import re
import requests
import time

class Playlist:
    def __init__(self, name, playlist_owner, playlist_id, auth_vals):
        self.name = name
        self.playlist_owner = playlist_owner
        self.playlist_id = playlist_id
        self.auth = auth_vals
        self.contents = self.get_contents()
        
    def get_contents(self):
        songs_url = "https://api.spotify.com/v1/users/" + self.playlist_owner + "/playlists/" + self.playlist_id + "/tracks"
        songs_values = self.auth.auth_dict
        songs_response = self.auth.http_request_response(songs_url, songs_values, 'GET')
        songs_dict = self.get_songs_from_playlist(songs_response)
        return songs_dict
        
    def get_songs_from_playlist(self, data):
        song_name = ''
        song_album = ''
        song_artists = []
        song = []
        songs_dict = {}
        songs_list = []
        song_val = {}
        for i in range(len(data['items'])):
                single_song_artists = []
                song_name = data['items'][i]['track']['name']
                song_album = data['items'][i]['track']['album']['name']
                for j in range(len(data['items'][i]['track']['artists'])):
                        single_song_artists.append(data['items'][i]['track']['artists'][j]['name'])
                song_artist = single_song_artists
                song.append(i)
                song.append(song_album)
                song.append(song_name)
                song.append(song_album)
                songs_list.append(song)
                songs_dict.update({i+1: {'name': song_name, 'artists': song_artist, 'album': song_album}})
        return songs_dict

