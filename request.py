#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import urlencode

login_link = 'forum.mxlinux.org/ucp.php?mode=login'


def get_html(url='', password=None, username=None):
    if password == None or username == None:
        return requests.get(url).text
    headers = {'User-Agent' : 'Mozilla/5.0'}
    payload = {'username': username, 'password': password, 'redirect':url, 'sid':'', 'login':'Login'}
    session = requests.Session()
    return session.post(login_link, headers=headers, data=payload).text

def get_url_arg(url, arg):
    parsed = urlparse.urlparse(url)
    return urlparse.parse_qs(parsed.query)[arg][0]

def set_url_arg(url, arg, val):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({arg : str(val)})
    url_parts[4] = urlencode(query)
    return urlparse.urlunparse(url_parts)

def get_only_pagination_number_buttons(tag):
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

# TODO improve merger
class Merge:
    def __init__(self, htmls=[]):
        if len(htmls) < 1:
            self.merged = ''
            return None
        text = ''.join(html for html in htmls)
        soup = BeautifulSoup(text, 'html.parser')
        text2 = ''.join(str(tag) for tag in list(soup.children))
        main_html = list(soup.children)[0]
        main_html.string = text2
        for tag in soup.children:
            if tag is not main_html:
                tag.extract()
        self.merged = str(soup)

class Request:
    def __init__(self, url='', pages=1, username=None, password=None):
        self.html = ''
        self.url = url
        html = get_html(url=self.url, password=password, username=username)
        parser = BeautifulSoup(html, 'html.parser')
        isMultiPage = False
        for pagination in parser.find_all('div', {'class' : 'pagination'}):
            isMultiPage = True
            break
        if not isMultiPage:
            self.html = html
            return None
        max_start = 0
        for pagination in parser.find_all('div', {'class' : 'pagination'}):
            for ul in pagination.find_all('ul'):
                for li in ul.find_all(get_only_pagination_number_buttons):
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
            page_count+=1
            start+=int(20 if typ == 'forum' else 10)
        merge = Merge(htmls=htmls)
        self.text = merge.merged

def get_all_forumbg(tag):
    if not tag.has_attr('class'):
        return False
    if 'forumbg' in tag['class']:
        return True
    if 'forabg' in tag['class']:
        return True

import argparse

parser = argparse.ArgumentParser()
parser.add_argument('url', help='Url for forum page')
parser.add_argument('--password', help='Password for your forum account')
parser.add_argument('--username', help='Username for your forum account')
parser.add_argument('--section', help='Name of section')
parser.add_argument('--amount', help='Amount of topics your want, default is 20')
args = parser.parse_args()

if args.amount == None:
    args.amount = 20

request = Request(url=args.url, pages=int(int(args.amount)/20)+1
soup = BeautifulSoup(request.text, 'html.parser')

section_map = {}

for forumbg in soup.fid_all(get_all_forumbg):
    for topiclist in soup.find_all('div', {'class' : 'topiclist'}):
        
        






