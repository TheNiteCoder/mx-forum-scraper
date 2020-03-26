
from bs4 import BeautifulSoup
import requests

class Session:
    def __init__(self):
        self.__password__ = None
        self.__username__ = None
        self.__session__ = requests.Session()
        self.__headers__ = {}
        self.__payload__ = {}
        self.__params__ = {}
    def login(self, url, username, password, usernamekey='username', passwordkey='password'):
        self.__password__ = password
        self.__username__ = username
        self.__headers__ = {"User-Agent" : "Mozilla/5.0"}
        self.__payload__ = {usernamekey : self.__username__, passwordkey : self.__password__}
        r = requests.post(url, headers=self.__headers__, data=self.__payload__)
        sidStart = r.text.find("sid")+4
        sid = r.text[sidStart:sidStart+32]
        self.__params__ = {'mode':'login', 'sid' : sid}
    def get(self, url):
        return requests.get(url, headers=self.__headers__, params=self.__params__, data=self.__payload__)

class Requestor:
    def __init__(self, session=None):
        self.__session__ = session
    def get(self, url):
        # TODO handle invalid requests e.g.  = 404
        html = None
        if self.__session__ == None:
            html = requests.get(url).text
        else:
            html = self.__session__.get(url).text
        return html

