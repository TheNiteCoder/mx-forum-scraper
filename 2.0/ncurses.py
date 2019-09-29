
import curses

import urwid

import forum, requestor

class Item:
    def text(self): 
        return self.__text
    def skip(self):
        return self.__skip
    def set_text(self, text):
        self.__text = text
    def set_skip(self, skip):
        self.__skip = skip

def main():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()

    stdscr.keypad(True)
    stdscr.clear()

    items = ['1', '2']
    updateNeeded = True
    position = 0
    c = stdscr.getkey()
    while c == 'q':
        if updateNeeded:
            stdscr.clear()
            for index, item in enumerate(items):
                if index >= position and index < stdscr.getmaxy() + position:
                    if index == position:
                        stdscr.attron(curses.A_REVERSE)
                    stdscr.addstr(item.text())
                    if index == position:
                        stdscr.attrof(curses.A_REVERSE)

    curses.endwin()

main()

