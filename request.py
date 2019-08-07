#!/usr/bin/python3

import requests

def get_html(url):
	return requests.get(url).text
