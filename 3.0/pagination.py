
from bs4 import BeautifulSoup, Tag, NavigableString
from strutil import extract

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



