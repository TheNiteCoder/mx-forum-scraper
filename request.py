#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import urllib.parse as urlparse
from urllib.parse import urlencode

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
	def __init__(self, url='', pages=1):
		self.html = ''
		self.url = url
		html = requests.get(self.url).text
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
			html = requests.get(page_url).text
			htmls.append(html)
			page_count+=1
			start+=int(20 if typ == 'forum' else 10)
		merge = Merge(htmls=htmls)
		self.text = merge.merged

'''
request = Request(url='https://forum.mxlinux.org/viewforum.php?f=107', pages=2)
with open('view.html', 'w') as f:
	f.write(request.text)
'''

headers = {'User-Agent' : 'Mozilla/5.0'}
payload = {'username' : 'username', 'password' : 'password' }
