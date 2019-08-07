
import requests
from bs4 import BeautifulSoup

class Scraper:
	def __init__(self, html='', url=''):
		self.html = html
		self.url = url
	def scrape_pages(self, amount=0, start=0):
		
