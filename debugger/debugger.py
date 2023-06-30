#!/usr/bin/env python3

import curses
from curses import wrapper
import random
import serial

stdscr = curses.initscr()
curses.start_color()

##############
#            #
#  Debugger  #
#            #
##############

class CommunicationException(Exception):
    pass

class Debugger:
    memory = [random.randint(0, 255) for _ in range(64 * 1024)]

    def send(self, cmd):
        self.ser.write(bytes(cmd + "\n", "latin1"))

    def recv(self):
        return self.ser.readline()

    def open_communication(self):
        self.ser = serial.Serial("COM6", 115200)
        self.send('h')  # request ACK
        print(self.recv())

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

    def key(self, c):
        if c == "KEY_NPAGE" or c == "KEY_UP":
            self.page -= 1
            if self.page < 0:
                self.page = 255
            self.draw()
        elif c == "KEY_PPAGE" or c == "KEY_DOWN":
            self.page += 1
            if self.page > 255:
                self.page = 0
            self.draw()


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
        stdscr.addstr(" [F1] Memory     [F2] Debugger    [F10] Quit")
        stdscr.refresh()
        if self.selected == "memory":
            self.memory.draw()

    def key(self, c):
        if c == curses.KEY_F1:
            self.selected = "memory"
        elif c == curses.KEY_F2:
            self.selected = "cpu"
        elif self.selected == "memory":
            self.memory.key(c)


def run_ui(stdscr):
    curses.noecho()
    curses.cbreak()
    curses.curs_set(False)
    stdscr.keypad(True)

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)

    main_screen = MainScreen()
    main_screen.initial_draw()

    while True:
        c = stdscr.getkey()
        if c == curses.KEY_F10:
            break
        else:
            main_screen.key(c)


##############
#            #
#    MAIN    #
#            #
##############

debugger = Debugger()
debugger.open_communication()
# wrapper(run_ui)
