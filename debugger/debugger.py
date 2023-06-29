#!/usr/bin/env python3

import curses
from curses import wrapper
import random

stdscr = curses.initscr()
curses.start_color()

##############
#            #
#  Debugger  #
#            #
##############

class Debugger:
    memory = [random.randint(0, 255) for _ in range(64 * 1024)]

debugger = Debugger()


##############
#            #
#     UI     #
#            #
##############

class MemoryScreen:

    page = 0

    def __init__(self, rows, cols):
        self.window = curses.newwin(rows - 1, cols, 1, 0)

    def draw(self):
        self.window.bkgd(curses.color_pair(1), curses.A_BOLD)
        for i in range(0, 16):
            addr = (self.page * 0x100) + (i * 0x10)
            self.window.addstr(i + 2, 4, "{:04X}  :".format(addr))
            for j in range(0, 16):
                x = 13 + (j * 3) + (0 if j < 8 else 1)
                self.window.addstr(i + 2, x, "{:02X}".format(debugger.memory[addr + j]))
        self.window.refresh()


class MainScreen:

    selected = "memory"

    def __init__(self):
        rows, cols = stdscr.getmaxyx()
        self.memory = MemoryScreen(rows, cols)

    def initial_draw(self):
        stdscr.bkgd(curses.color_pair(1), curses.A_BOLD)
        stdscr.clear()
        stdscr.chgat(0, 0, -1, curses.color_pair(2))
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(" [F1] Memory     [F2] Debugger")
        stdscr.refresh()
        if self.selected == "memory":
            self.memory.draw()


def run_ui(stdscr):
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    stdscr.keypad(True)

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)

    main_screen = MainScreen()
    main_screen.initial_draw()

    stdscr.getkey()


##############
#            #
#    MAIN    #
#            #
##############

debugger = Debugger()
wrapper(run_ui)
