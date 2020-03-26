
from pagination import Pagination
from requestor import Requestor
from bs4 import BeautifulSoup, NavigableString
import soupsieve as sv

from urlutil import set_url_arg

from strutil import extract, extact_code, stringify

class SubForum:
    def __init__(self, link, req=Requestor()):
        self.link = link
        self.pag = Pagination(req.get(link)) 
        self.pages = SubForumPages(self.link, pag=self.pag)

class SubForumPage:
    def __init__(self, link, req=Requestor(), index=0):
        self.source = req.get(link)
        self.index = index
        self.sections = []
        self.__build()
    def __build(self):
        soup = BeautifulSoup(self.source, 'html.parser')
        for section in soup.select('div:is(.forumbg, .forabg)'):
            section_obj = Section(items=[])
            header = section.select_one('li.header')
            section_title_element = header.select_one('div.list-inner')
            section_obj.title = extract(section_title_element)
            for listitem in section.select('li'): # could change to li but bug fixing is necesary
                obj = None 
                title = ''
                link = ''
                isBig = False
                if listitem.select_one('a.topictitle') is not None:
                    isBig = len(listitem.select('a.topictitle')) > 1
                elif listitem.select_one('a.forumtitle') is not None:
                    isBig = len(listitem.select('a.forumtitle')) > 1
                if isBig:
                    continue
                if listitem.select_one('a.topictitle') is not None:
                    title_element = listitem.select_one('a.topictitle') # Handling if we grab something wrong like the section headers 
                    if title_element is None: 
                        # print('title_element is None')
                        # print(str(listitem)) 
                        continue 
                    link = title_element['href'] 
                    title = extract(title_element).strip()
                    obj = TopicView(link=link)
                else:
                    obj = SubForumView(link=link)
                    title_element = listitem.select_one('a.forumtitle')
                    if title_element is None:
                        continue
                    link = title_element['href']
                    title = extract(title_element).strip()
                    obj = SubForumView(link=link)
                title = extract(title_element).strip()
                obj.title = title
                section_obj.items.append(obj)
            self.sections.append(section_obj)



class SubForumPages:
    def __init__(self, base, pag=None, interval=20):
        self.pag = pag
        self.current_page = 1
        self.interval = 20
        self.base = base
    def reset(self):
        self.current_page = 0
    def __iter__(self):
        self.reset()
        return self
    def __next__(self):
        if self.current_page >= self.pag.number_of_pages():
            raise StopIteration
        
        obj = SubForumPage(set_url_arg(self.base, 'start', self.current_page * self.interval), index=self.current_page)

        self.current_page += 1

        return obj
    def at(self, idx):
        if idx >= self.pag.number_of_pages():
            return None
        obj = SubForumPage(set_url_arg(self.base, 'start', idx * self.interval), index=idx)
        return obj

class TopicView:
    def __init__(self, title=None, link=None, unread=False):
        self.title = title
        self.link = link
        self.unread = unread

class SubForumView:
    def __init__(self, title=None, link=None):
        self.title = title
        self.link = link

class Section:
    def __init__(self, title=None, items=None):
        self.title = title
        self.items = items
    def __iter__(self):
        return self.items

class Post:
    def __init__(self, username=None, title=None, body=None):
        self.username = username
        self.title = title
        self.body = body

class Topic:
    def __init__(self, link, req=Requestor()):
        self.req = req
        self.pag = Pagination(self.req.get(link))
        self.pages = TopicPages(link, pag=self.pag)

class TopicPage:
    def __init__(self, link, index=0, req=Requestor()):
        self.req = req
        self.source = req.get(link)
        self.posts = []
        self.__build()
    def __build(self):
        soup = BeautifulSoup(self.source, 'html.parser')
        for post in soup.select('div.post'):
            obj = Post()
            h3_title_anchor = post.select_one('h3')
            obj.title = extract(h3_title_anchor.a)
            content = post.select_one('div.content') 
            obj.body = extract(content)
            postprofile = post.select_one('dl.postprofile')
            anchor_username = postprofile.select_one('a[class*="username"]')
            obj.username = extract(anchor_username)
            self.posts.append(obj)
    def __iter__(self):
        return iter(self.posts)

class TopicPages:
    def __init__(self, base, pag=None, interval=10):
        self.pag = pag
        self.current_page = 1
        self.interval = interval
        self.base = base
    def reset(self):
        self.current_page = 0
    def __iter__(self):
        self.reset()
        return self
    def __next__(self):
        if self.current_page >= self.pag.number_of_pages():
            raise StopIteration
        obj = TopicPage(set_url_arg(self.base, 'start', self.current_page * self.interval), index=self.current_page)
        self.current_page += 1
        return obj

    def at(self, idx):
        if idx >= self.pag.number_of_pages():
            return None
        obj = TopicPage(set_url_arg(self.base, 'start', idx * self.interval), index=idx)
        return obj

