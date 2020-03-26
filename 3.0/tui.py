
import requestor 
import phpbb
from itertools import repeat
import getpass

import sys, os
import subprocess

import urwid

# out = open('log', 'a')

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
            body.append(urwid.Padding(urwid.Pile([urwid.Text(u'Code'), urwid.Text(source)], align=urwid.CENTER, left=1, right=1)))
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


class TopicBrowser(urwid.Pile):
    def __init__(self, topic):
        self.current_page = 0
        self.topic = topic
        self.back_btn = urwid.Button(u'Back')
        urwid.connect_signal(self.back_btn, 'click', self.back_page)
        self.back_btn = urwid.AttrMap(self.back_btn, 'btn', focus_map='reversed')
        self.next_btn = urwid.Button(u'Next')
        urwid.connect_signal(self.next_btn, 'click', self.next_page)
        self.next_btn = urwid.AttrMap(self.next_btn, 'btn', focus_map='reversed')
        body = [self.back_btn, self.next_btn]
        super(TopicBrowser, self).__init__(body)
        self.regen()
    def regen(self):
        page = self.topic.pages.at(self.current_page)
        if page is None:
            return
        page_browser = create_topic_browser(u'Browser', page)
        self.widget_list[:] = [urwid.BoxAdapter(page_browser, self.__calculate()), self.back_btn, self.next_btn]
    def __calculate(self):
        # Calulate the size of the Viewer
        raw = subprocess.check_output(['tput', 'lines'])
        rows = int(raw)
        return rows - 3
    def next_page(self, button):
        if self.current_page >= self.topic.pages.pag.number_of_pages():
            return
        self.current_page += 1
        self.regen()
    def back_page(self, button):
        if self.current_page == 0:
            return
        self.current_page -= 1
        self.regen()

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
        if type(self.obj) is phpbb.SubForum:
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
            self.obj = phpbb.SubForum(link)
        else:
            self.obj = phpbb.Topic(link)
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

session = requestor.Session()

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

req = requestor.Requestor(session=session)

#topic = phpbb.SubForum('https://forum.mxlinux.org/viewforum.php?f=104')
topic = phpbb.SubForum('https://forum.mxlinux.org')

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

