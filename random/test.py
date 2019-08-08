from bs4 import BeautifulSoup
import requests
from page import Page

# has to handle mutli page things
class Forum:
	def __init__(self, html='', url='', name=''):
		self.html = html
		self.url = url
		self.name = name
		self.sections = []
	def grab(self, amount=0, start=0, name=''):
		page = Page(url=self.url)
		sections = page.grab(tag='div', tag_attrs={'class' : 'forumbg'})
		section_objs = []
		for section in sections:
			section_obj = Section(html=section)
			section_obj.get_metadata()
			flag = True
			for section_com in section_objs:
				if section_com.name == section_obj.name:
					section_com.html += section_obj.html
					flag = False
			if flag:
				section_objs.append(section_obj)
		self.sections.extend(section_objs)
		
class Section:
	def __init__(self, html='', name=''):
		self.html = html
		self.name = name
		self.items = []
	def get_metadata(self):
		parser = BeautifulSoup(self.html, 'html.parser')
		for title in parser.find_all('div', {'class' : 'list-inner'}):
			self.name = title.contents[0]
	def get_items(self):
		parser = BeautifulSoup(self.html, 'html.parser')
		for lis = parser.find_all('div', {'class' : 'list-inner'}):
			for li in lis.find_all('li'):
				for title in li.find_all('a', {'class' : 'topictitle'}):
					obj = None
					if title['href'].find('viewforum') != -1:
						obj = Forum(url=title['href'], name=title.contents[0])
					else:
						obj = Topic(url=title['href'], name=title.contents[0])
					items.append(obj)
		
# has to handle multi page things
class Topic:
	def __init__(self, url='', title='', html=''):
		self.url = url
		self.title = title
		self.html = html
	def grab(self, amount=0, start=0):
		page = Page(url=self.url)
		posts = page.grab(tag='div', tag_attrs={'class' : 'post'})
		for post in posts:
			
class User:
	def __init__(self, name='', joined='', posts=''):
		self.name = name
		self.joined = joined
		self.posts = posts

# doesn't have to handle multi page things
class Post:
	def __init__(self, user=User(), title='', body='']]
	
	):
