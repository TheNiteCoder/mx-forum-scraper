
import requests
from bs4 import BeautifulSoup 

def __util_get_all_forumbg(tag):
    if not tag.has_attr('class'):
        return False
    if 'forumbg' in tag['class']:
        return True
    elif 'forabg' in tag['class']:
        return True
    return False

def __util_get_only_pagination_number_buttons(tag):
    if tag.a == None:
        return False
    if not tag.a.has_attr('class'):
        return False
    if not 'button' in tag.a['class']:
        return False
    if not tag.a.has_attr('role'):
        return False
    if not 'button' in tag.a['role']:
        return False
    if not tag.a.has_attr('href'):
        return False
    if tag.a['href'] == '#':
        return False
    if tag.has_attr('class'):
        return False
    return True

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

# TODO: abstract the Requestor class so it doesn't depend on parsing html itself

class Requestor:
    def __init__(self, session=None):
        self.__session__ = Session()
    def request(self, url, pages=1):
        html = ''
        if self.__session__ == None:
            html = requests.get(url).text
        else:
            html = self.__session__.get(url).text
        parser = BeautifulSoup(html, 'html.parser')
        is_multi_page = False
        for pagination in parser.find_all('div', {'class' : 'pagination'}):
            is_multi_page = True
            break
        if not is_multi_page:
            return [html] # return as list
        max_start = 0
        for pagination in parser.find_all('div', {'class' : 'pagination'}):
            for ul in pagination.find_all('ul'):
                for li in ul.find_all(__util_hget_only_pagination_number_buttons):
                    max_start = max(max_start, int(li.find_all('a')[0].string))
                break
        typ = ''
        if url.find('viewtopic') != -1:
            typ = 'topic'
        else:
            typ = 'forum'
        page_count = 0
        start = 0
        htmls = []
        while page_count < pages:
            page_url = self.url
            page_url = set_url_arg(page_url, 'start', start)
            html = get_html(url=page_url, password=password, username=username)
            htmls.append(html)
            page_count += 1
            start += int(20 if typ == 'forum' else 10)
            return htmls


