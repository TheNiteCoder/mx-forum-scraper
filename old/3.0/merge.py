#!/usr/bin/python3

# REQUIRES bs4, soupsieve, urwid

from itertools import repeat
import getpass

import sys, os
import subprocess

import urwid

# out = open('log', 'a')

from bs4 import BeautifulSoup, NavigableString
import soupsieve as sv

from bs4 import BeautifulSoup, Tag, NavigableString

from bs4 import NavigableString, BeautifulSoup, Tag, Comment
import soupsieve as sv

from urllib import parse as urlparse

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


def set_url_arg(url, arg, val):
    url_parts = list(urlparse.urlparse(url))
    query = dict(urlparse.parse_qsl(url_parts[4]))
    query.update({arg : str(val)})
    url_parts[4] = urlparse.urlencode(query)
    return urlparse.urlunparse(url_parts)

def stringify(tag):
    # return str(tag.encode('utf-8'))
    return str(tag)

def extact_code(code):
    content = code.select_one('code')
    return extract(content)

def extract(tag):
    if type(tag) is NavigableString:
        return stringify(tag)
    if type(tag) is Comment:
        return str()
    text = ''
    for item in tag.contents:
        if type(item) is NavigableString:
            text += stringify(item)
        elif type(item) is Comment:
            pass
        elif item.name == 'br':
            text += '\n'
        elif item.name == 'p':
            text += '\n'
            text += extract(item)
        elif item.name == 'b':
#            text += '[b]'
            text += extract(item)
#            text += '[/b]'
#        elif item.name == 'i':
#            text += '[i]'
#            text += extract(item)
#            text += '[/i]'
        elif sv.match('div.codebox', item):
            text += '[code]'
            text += extact_code(item)
            text += '[/code]'
        else:
            text += '\n'
            text += extract(item) 
    return text



class Pagination:
    def __init__(self, page):
        self.__max_pages__ = 0
        self.refresh(page)
    def refresh(self, source):
        soup = BeautifulSoup(source, 'html.parser')
        pagination = soup.select_one('div:is(.pagination) ul')
        if pagination is None:
            self.__max_pages__ = 1
            return
        items = []
        for item in pagination.contents:
            items.append(item)
        last = items[len(items)-4]
        if type(last) is not Tag or last.name != 'li':
            print('pagination: internal error: could not find last li item')
            self.__max_pages__ = 1
            return
        self.__max_pages__ = int(extract(last))

    def old_refresh(self, source):
        soup = BeautifulSoup(source, 'html.parser')
        pagination = soup.select_one('div:is(.pagination) ul')
        if pagination is None:
            self.__max_pages__ = 1
            return
        ellipsis = pagination.select_one('li.ellipsis')
        if ellipsis is None:
            self.__max_pages__ = 1
            return
        last = ellipsis.find_next('li')
        if last is None:
            self.__max_pages__ = 1
            return
        button = last.a
        if button is None:
            self.__max_pages__ = 1
            return
        self.__max_pages__ = int(button.string)
    def number_of_pages(self):
        return self.__max_pages__



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


def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

def menu(title, items, item_chosen_hander):
    body = [urwid.Text(title), urwid.AttrMap(urwid.Divider(), 'divider')]
    for item in items:
        button = urwid.Button(item)
        urwid.connect_signal(button, 'click', item_chosen_hander)
        body.append(urwid.AttrMap(button, None, focus_map='reversed')) 
    return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def find_markup(source, tag):
    formed_tag = '[{}]'.format(tag)
    if source.find(formed_tag) == -1:
        return -1
    return source.find(formed_tag)

def render_post(source):
    # returns urwid.Pile 
    body = []
    while True:
        pos = find_markup(source, 'code')
        if pos == -1:
            body.append(urwid.Text(source))
            break
        before_text = source[:pos-1]
        body.append(urwid.Text(before_text))
        source = source[pos+len('[{}]'.format('code')):]
        endpos = find_markup(source, '/code')
        if endpos == -1:
#            body.append(urwid.Padding(urwid.Pile([urwid.Text(u'Code'), urwid.Text(source)], align=urwid.CENTER, left=1, right=1)))
            pass
        else:
            codebody = body[:endpos-1]
            source = source[:len('[{}]'.format('/code'))]
            if len(codebody) == 0:
                continue
#            try:
#                body.append(urwid.Padding(urwid.Pile([urwid.Text(u'Code'), urwid.Text(codebody)]))) 
#            except:
#                out.write('\n' + codebody + '\n')
    return urwid.Pile(body)

class ForumBrowser(urwid.Pile):
    def __init__(self, forum):
        self.current_page = 0
        self.history = [forum.link]
        self.back_btn = urwid.Button(u'Back')
        urwid.connect_signal(self.back_btn, 'click', self.back_page)
        self.back_btn = urwid.AttrMap(self.back_btn, 'btn', focus_map='reversed')
        self.next_btn = urwid.Button(u'Next')
        urwid.connect_signal(self.next_btn, 'click', self.next_page)
        self.next_btn = urwid.AttrMap(self.next_btn, 'btn', focus_map='reversed')
        self.obj = forum
        body = [self.back_btn, self.next_btn]
        super(ForumBrowser, self).__init__(body)
        self.regen()
    def regen(self):
        if type(self.obj) is SubForum:
            viewer = self.create_forum_browser(u'Title', self.obj.pages.at(self.current_page))
        else:
            viewer = self.create_topic_browser(u'Title', self.obj.pages.at(self.current_page))
        self.widget_list[:] = [urwid.BoxAdapter(viewer, self.__calculate()), self.back_btn, self.next_btn]
    def __calculate(self):
        # Calulate the size of the Viewer
        raw = subprocess.check_output(['tput', 'lines'])
        rows = int(raw)
        return rows - 3
    def next_page(self, button):
        if self.current_page >= self.obj.pages.pag.number_of_pages()-1:
            return
        self.current_page += 1
        self.regen()

    def back_page(self, button):
        if self.current_page == 0:
            if len(self.history) > 1:
                item = self.history[len(self.history)-2]
                self.history = self.history[:len(self.history)-2]
                self.handle_nav(item, None)
            else:
                return
        self.current_page -= 1
        self.regen()
    def __fix_link(self, link):
        return 'https://forum.mxlinux.org' + link[1:]
    def handle_nav(self, link, btn):
        self.history.append(link)
        self.current_page = 0
        if str(link).find('viewtopic') == -1: 
            # Forum view
            self.obj = SubForum(link)
        else:
            self.obj = Topic(link)
        self.regen()
    def create_forum_browser(self, title, forum):
        # body = [urwid.Text(title), urwid.AttrMap(urwid.Divider('='), 'divider')]
        body = []
        for section in forum.sections:
            body.append(urwid.AttrMap(urwid.Text(section.title), 'post_title'))
            for topic in section.items:
                btn = urwid.Button(topic.title)
                urwid.connect_signal(btn, 'click', self.handle_nav, user_args=[self.__fix_link(topic.link)])
                btn = urwid.AttrMap(btn, 'post_body')
                body.append(btn)
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))
    def create_topic_browser(self, title, topic):
        # body = [urwid.Text(title), urwid.AttrMap(urwid.Divider('='), 'divider')]
        body = []
        for post in topic.posts:
            title_part = urwid.AttrMap(urwid.Text(post.title + ' - ' + post.username), 'post_title')
            body_part = urwid.AttrMap(urwid.Text(post.body), 'post_body')
            body.append(title_part)
            body.append(body_part)
            body.append(urwid.AttrMap(urwid.Divider(u'*'), 'divider'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

def item_chosen(button):
    raise urwid.ExitMainLoop()

session = Session()

username = input('Username: ')
password = None
try:
    password = getpass.getpass()
except Exception as error:
    print('Error getting password:', error)
    sys.exit(-1)

if password is None:
    print('Password is NULL or None')
    sys.exit(-1)

session.login('https://forum.mxlinux.org/login.php', username, password)

req = Requestor(session=session)

#topic = phpbb.SubForum('https://forum.mxlinux.org/viewforum.php?f=104')
topic = SubForum('https://forum.mxlinux.org')

palette = [
    ('post_title', '', '', '', '#000', '#7AF'),
    ('post_body', '', '', '', '#000', '#FFF'),
    ('btn', '', '', '', '#000', '#7AF'),
    ('divider', '', '', '', '#000', '#000')
]

header = urwid.AttrMap(urwid.Text(u'MX Forum TUI', align=urwid.CENTER), 'header')

browser = ForumBrowser(topic)

content = [header, browser]

pile = urwid.Pile(content)

main_widget = urwid.Filler(pile, 'top')

main = urwid.Padding(main_widget, left=2, right=2)
loop = urwid.MainLoop(main, palette=palette, unhandled_input=exit_on_q)
loop.screen.set_terminal_properties(colors=256)
loop.run()

# out.close()

