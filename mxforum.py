#!/usr/bin/python3

import requests
from bs4 import BeautifulSoup
import re as regex
import urllib.urlparse as urlparse

def get_html(url):
	return requests.get(url).text

def get_is_multi_page(html):
	flag = False
	soup = BeautifulSoup(html, 'html.parser')
	for pagination in soup.find_all('div', {'class' : 'pagination'}):
		flag = True
	return flag

topic_interval = 10
forum_interval = 20
		
def set_url_arg(url, arg, val):
	url_parts = list(urlparse.urlparse(url))
	query = dict(urlparse.parse_qsl(url_parts[4]))
	query.update({arg : str(val)})
	url_parts[4] = urlencode(query)
	return urlparse.urlunparse(url_parts)

class Forum:
	def __init__(self, url='', name=''):
		self.url = url
		self.name = name
		self.sections = []
	def grab_sections(self, amount=0, start=0):
		count = 0
		acount = 0
		page = 0
		started = False
		while acount < amount:
			url = self.url
			url = set_url_arg(url, 'start', page*forum_interval)
			html = requests.get(url).text
			soup = BeautifulSoup(html, 'html.parser')
			for forumbg in soup.find_all('div', {'class':'forumbg'}):
				for title in forumbg.find_all('div', {'class':'list-inner'})
		
