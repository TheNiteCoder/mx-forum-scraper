
import curses

def main(stdscr):
    
    has_color = curses.has_colors()

    height, width = stdscr.getmaxyx()

    viewport = curses.newwin(height, width)
    viewport.border()

    stdscr.refresh()
    viewport.refresh()

    color_pairs = {
            'heading' : 1,
    }

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_WHITE)

    stdscr.keypad(True)

    while True:

        stdscr.refresh()
        viewport.refresh()

       

curses.wrapper(main)

