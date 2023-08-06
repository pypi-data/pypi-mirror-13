import os
import urllib
import urllib2
import re
import requests
import time

class Song:
    def __init__(self, name, artists, album):
        self.name = name
        self.artists = " ".join(artists)
        self.album = album
        
    def get_youtube_mp3_url(self, url):
        for i in xrange(2):
            statusurl = None
            r = requests.post("http://www.listentoyoutube.com/cc/conversioncloud.php", data={"mediaurl": url, "client_urlmap": "none"})
            try:
                statusurl = eval(r.text)['statusurl'].replace('\\/', '/') + "&json"
                break
            except:
                print eval(r.text)['error']
                time.sleep(1)
        while True:
            if not statusurl:
                #raise Exception("")
		downloadurl = None
		break
            try:
                resp = eval(requests.get(statusurl).text)
                if 'downloadurl' in resp:
                    downloadurl = resp['downloadurl'].replace('\\/', '/')
                    break
                time.sleep(1)
            except Exception:
                pass
        return downloadurl
        
    def download(self, folder):
        youtube_url = "http://www.youtube.com/"
        r = requests.get(youtube_url + "results?", params={"search_query": "%s %s" % (self.name, self.artists)}).text
        top_vid_id = re.findall(r'data-context-item-id="(.*?)"', r)[1]
        mp3_url = self.get_youtube_mp3_url(youtube_url + "watch?v=" + top_vid_id)
        if not mp3_url:
		print "could not download %s" % self.name
		return
        cmd = 'cd %s && wget --show-progress %s' % (folder, mp3_url)
        os.system(cmd)
        
    #show time/progress bar decorator?
