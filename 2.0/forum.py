
import requestor

def selector(obj):
    return obj.selector

class ConstructError(BaseException):
    def __init__(self, msg):
        self.__msg__ = msg
    def __str__(self):
        return self.__msg__

class ForumObject:
    def __init__(self, selectors=dict()):
        self.__selectors__ = selectors
        # self.selector = dict()
        # keys
        # 'global' : detect if reading whole document
        # 'section' : detect if reading from a section object's html
        # etc
    def selector(self, name='global'):
        if not name in self.__selectors__.keys():
            return None
        return self.__selectors__[name]
        

class Section(ForumObject):
    def __init__(self):
        super().__init__({'global' : 'div:is(.forabg, .forumbg)'})
        self.link = ''
        self.title = ''
        self.items = []
    def construct(self, html, construct_with_topic_and_forum_views=False):
        parser = requestor.BeautifulSoup(html, 'html.parser')
        title_element = parser.select_one('div:is(.inner) ul:is(.topiclist) li:is(.header) dl:is(.row-item) dt div:is(.list-inner)')
        if title_element == None:
            raise ConstructError('title_element == None')
        if not title_element.find('a') == None:
            title_element = title_element.a
        if title_element.has_attr('href'):
            self.link = title_element['href']
        self.title = title_element.text
        self.title = self.title.strip()
        if construct_with_topic_and_forum_views:
            for match in parser.select(ForumView().selector('section')):
                fv = ForumView()
                try:
                    fv.construct(str(match))
                    self.items.append(fv)
                except ConstructError:
                    raise ConstructError('fv.construct threw ContructError: ')
            for match in parser.select(TopicView().selector('section')):
                tv = TopicView()
                try:
                    tv.contruct(str(match))
                    self.items.append(tv)
                except ConstructError:
                    raise ConstructError('tv.construct threw ConstructError: ')


class TopicView(ForumObject):
    def __init__(self):
        super().__init__({'global' : 'div:is(.forabg, .forumbg) ul li:has(a:is(.topictitle)):not(.row)',
                          'section' : 'ul li:has(a:is(.topictitle):not(.row))'})
        self.link = ''
        self.title = ''
    def contruct(self, html):
        if html == None:
            raise ConstructError('html == None')
        parser = requestor.BeautifulSoup(html, 'html.parser')
        topictitle = parser.select_one('a:is(.topictitle)')
        if topictitle == None:
            raise ConstructError('topictitle == None')
        if not topictitle.has_attr('href'):
            raise ConstructError('not topictitle.has_attr(\'href\')')
        self.link = topictitle['href']
        i = topictitle.find('i')
        if i != None:
            i.decompose()
        self.title = topictitle.text
        self.title = self.title.strip()

class ForumView(ForumObject):
    def __init__(self):
        super().__init__({'global' : 'div:is(.forabg, .forumbg) ul:is(.topiclist) li:is(.row) dl:is(.row-item) dt div:is(.list-inner)',
                          'section' : 'ul:is(.topiclist) li:is(.row) dl:is(.row-item) dt div:is(.list-inner)'})
        self.title = ''
        self.link = ''
    def construct(self, html):
        p1 = requestor.BeautifulSoup(html, 'html.parser')
        title_link = p1.select_one('a:is(.forumtitle)')
        if title_link == None:
            raise ConstructError('title_link == None')
        if title_link.has_attr('href'):
            self.link = title_link['href']
        self.title = title_link.text
        self.title = self.title.strip()


