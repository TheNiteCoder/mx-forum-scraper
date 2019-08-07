
from bs4 import BeautifulSoup
import requests
import urllib.parse as urlparse
from urllib.parse import urlencode

class Page:
	def __init__(self, url=''):
		self.max_start = 0 
		self.url = url
		self.update_html()
		self.update_metadata()
		self.html = ''
	def update_html(self):
		self.html = requests.get(self.url).text
	def update_metadata(self):
		parser = BeautifulSoup(self.html, 'html.parser')
		max_start = 0
		for pagination in parser.find_all('div', { 'class' : 'pagination' }):
			for ul in pagination.find_all('ul'):
				for li in ul.find_all('li'):
					if len(li.find_all('a', {'role' : 'button', 'class' : 'button'})) > 0:
						if li.a['href'] == '#':
							continue
						parsed = urlparse.urlparse(li.a['href'])
						if max_start < int(urlparse.parse_qs(parsed.query)['start'][0]):
							max_start = int(urlparse.parse_qs(parsed.query)['start'][0])
			break
		if max_start == 0:
			self.max_start = 0
		else:
			self.max_start = max_start + 20

	def grab(self, tag='', tag_attrs={}, amount=None, start=0):
		count = 0
		lstart = start
		tags = []
		while lstart <= self.max_start:
			url_parts = list(urlparse.urlparse(self.url))
			query = dict(urlparse.parse_qsl(url_parts[4]))
			query.update({'start' : str(lstart)})
			url_parts[4] = urlencode(query)
			tmp_url = urlparse.urlunparse(url_parts)
			data = requests.get(tmp_url)
			soup = BeautifulSoup(data.text, 'html.parser')
			for tag in soup.find_all(tag, tag_attrs):
				if amount != None:
					if count >= amount:
						return tags
					else:
						tags.append(tag)
						count+=1
				else:
					tags.append(tag)
					count+=1
			lstart += 20
		return tags	
