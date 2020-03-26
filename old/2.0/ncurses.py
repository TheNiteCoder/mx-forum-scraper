#!/usr/bin/python3
import forum, requestor
import math
import curses
import sys
import os

class CursesMenu:
    def __init__(self, win, options):
        self.__window = win
        self.__window.clear()
        self.__window.box()
        self.__options = options
        self.__window_offset = 1
        self.__max_row = self.__window.getmaxyx()[0] #- (self.__window_offset * 2)
        self.__pages = int( math.ceil(len(self.__options)) )
        self.__position = 1
        self.__page = 1
    def update(self, key):
        if key == curses.KEY_DOWN:
            if self.__page == 1:
                if self.__position < i:
                    self.__position = self.__position + 1
                else:
                    if self.__pages > 1:
                        self.__page = self.__page + 1
                        self.__position = 1 + (self.__max_row * (self.__page - 1))
            elif self.__page == self.__pages:
                if self.__position < len(self.__options):
                    self.__position = self.__position + 1
            else:
                if self.__position < self.__max_row + (self.__max_row * (self.__page - 1)):
                    self.__position += 1
                else:
                    self.__page += 1
                    self.__position = 1 + (self.__max_row * (self.__page - 1))
        if key == curses.KEY_UP:
            if self.__page == 1:
                if self.__position > 1:
                    self.__position = self.__position - 1
            else:
                if self.__position > ( 1 + ( self.__max_row * ( self.__page - 1 ) ) ):
                    self.__position = self.__position - 1
                else:
                    self.__page = self.__page - 1
                    self.__position = self.__max_row + ( self.__max_row * ( self.__page - 1 ) ) 
        if key == ord('\n') and self.__position != 0:
            return False
        for i in range(1, self.__max_row + 1):
            if i == self.__position:
                self.__window.addstr(i, 2, self.__options[i - 1])
            if i == len(self.__options):
                break
        self.__window.refresh()
        return True

        
        

def main(stdscr):
    curses.noecho()
    curses.cbreak()

    stdscr.keypad(True)
    stdscr.clear()

    cm = CursesMenu(stdscr, ['a', 'b', 'c'])
    
    rtn = True
    while rtn:
        rtn = cm.update(stdscr.getkey())
    

curses.wrapper(main)


