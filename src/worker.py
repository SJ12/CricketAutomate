'''
Created on May 2, 2015

@author: ROBINHOOD
'''
import urllib
from django.utils import simplejson as json
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import memcache
import logging

class MainPage(webapp.RequestHandler):
    
    def get(self):
#         self.get_match_with_alerts()
        
        if self.request.get("check"):
            self.check_for_live_match()
            
        if self.request.get("push"):
            self.do_push()
        
    def get_match_with_alerts(self):
        # Add a value if it doesn't exist in the cache, with a cache expiration of 1 hour.
        data = json.loads(urllib.urlopen("http://mapps.cricbuzz.com/cbzandroid/2.0/currentmatches.json").read())
        alert_matches=[]
        match_start_time=[]
        for ele in data:
            if ele.get('header').get('mchState') not in "complete":
                if ele.get("valueAdd"):
                    if ele.get("valueAdd").get("alerts").get("enabled")=="1":
                        alert_matches.append(ele.get("matchId"))
                        match_start_time.append(ele.get('header').get('startdt')+" "+ele.get('header').get('stTme'))
        if len(alert_matches)>0:        
            memcache.set_multi({"matchId":",".join(alert_matches),"time":",".join(match_start_time)})
            
    def check_for_live_match(self):
        data = json.loads(urllib.urlopen("http://mapps.cricbuzz.com/cbzandroid/2.0/currentmatches.json").read())
        for ele in data:
             if ele.get("valueAdd"):
                    if ele.get("valueAdd").get("alerts").get("enabled")=="1":
                        if ele.get('header').get('mchState') not in ["complete","preview","stump"]:
                            logging.info(ele.get("matchId"))
                            memcache.set("live","1")
                            logging.info("live")
                            break
        else:
             logging.info("no live")
             memcache.set("live","0")
             
             
    def do_push(self):
        live = memcache.get("live")
        
        if live is "1":
            data = urllib.urlopen("http://cricketpush12.appspot.com").read()
application = webapp.WSGIApplication([
    ('/', MainPage)
], debug=True)

# check_live = webapp.WSGIApplication([
#     ('/check', MainPage)
# ], debug=True)

def main():
    if application:
        run_wsgi_app(application)
 
if __name__ == "__main__":
    main()