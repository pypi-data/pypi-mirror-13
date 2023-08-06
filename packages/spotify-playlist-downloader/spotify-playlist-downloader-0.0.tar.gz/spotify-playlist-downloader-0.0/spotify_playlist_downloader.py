#!/usr/bin/python

import os
import urllib
import urllib2
import re
import requests
import time

import song
import playlist
import playlists
import auth

def main():
	a = auth.Auth()
	username = raw_input("Spotify Username: ")
	ps = playlists.Playlists(username, a)
	ps.display_playlists() #with numbers
	playlist_choice = int(raw_input("Which playlist would you like to download? "))-1
	p = playlist.Playlist(ps.playlist_names[playlist_choice], ps.playlist_owners[playlist_choice], ps.playlist_ids[playlist_choice], a)
	cmd = 'mkdir %s' % (ps.playlist_names[playlist_choice].replace(" ", ""))
	os.system(cmd)
	def tmp(val):
	    s = Song(val["name"], val["artists"], val["album"])
 	    s.download()
 	    print val["name"] + "...DONE!!!"
	#pool = ThreadPool(4) 
	# Open the urls in their own threads
	# and return the results
	#results = pool.map(tmp, p.contents.values())
	#close the pool and wait for the work to finish 
	#pool.close() 
	#pool.join()
	for val in p.contents.values():
	    s = song.Song(val["name"], val["artists"], val["album"])
	    s.download(ps.playlist_names[playlist_choice].replace(" ", ""))
	    print val["name"] + "...DONE!!!"

if __name__ == "__main__": main()

