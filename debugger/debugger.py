#!/usr/bin/env python3

import curses
from curses import wrapper
import os
import random
import re
import serial
import subprocess
import time
import sys

##############
#            #
#  Compiler  #
#            #
##############

def compile_source(source_filename):
    cp = subprocess.run(['./vasmz80_oldstyle', '-chklabels', '-L', 'listing.txt', '-Llo', '-nosym', '-x', '-Fbin', '-o', 'rom.bin', source_filename], capture_output=True, text=True)
    print(cp.stdout)
    if cp.stderr != '':
        print(cp.stderr)
    if cp.returncode != 0:
        exit(1)
    dbg_source = ''
    rom = None
    with open('listing.txt', 'r') as f:
        dbg_source = f.read()
    if os.path.exists('listing.txt'):
        os.remove('listing.txt')
    with open('rom.bin', 'rb') as f:
        rom = bytearray(f.read())
    if os.path.exists('rom.bin'):
        os.remove('rom.bin')
    if cp.stderr != '':
        input('\nPress any key to continue...')
    return dbg_source, rom


##############
#            #
#  Debugger  #
#            #
##############

class CommunicationException(Exception):
    pass

class Debugger:
    memory = [0xff for _ in range(64 * 1024)]
    pc = 0
    source = []
    source_map = {}
    source_map_pc = {}

    def update_source(self, src):
        self.source = src.split("\n")
        pattern = r"^[0-9A-Fa-f]{4}$"
        i = 0
        for line in self.source:
            address = line[3:7]
            if re.match(pattern, address):
                self.source_map[i] = int(address, 16)
                self.source_map_pc[int(address, 16)] = i
            i += 1

    def send(self, cmd):
        # print("> " + cmd)
        self.ser.write(bytes(cmd + '\n', 'latin1'))

    def recv(self):
        b = self.ser.readline().decode('latin1').replace('\n', '').replace('\r', '').split()
        # print("< ", b)
        if len(b) > 0 and b[0] == 'x':
            raise Exception('Debugger responded with error')
        return b

    def ack(self):
        self.send('h')
        self.recv()

    def reset(self):
        self.send('R')
        self.recv()
        self.next()

    def next(self):
        self.send('n')
        self.pc = int(self.recv()[0])

    def emulate_keypress(self, key):
        self.send('U %d' % (key & 0xff))

    def upload_rom(self, rom):
        for i in range(0, len(rom), 16):
            bts = rom[i:(i+16)]
            request = ('w %d %d ' % (i, len(bts))) + ' '.join([str(x) for x in bts])
            self.send(request)
            self.recv()
            print('.', end='')
        print()

    def update_memory_page(self, page):
        self.send('r %d 256' % (page * 0x100))
        self.memory[(page * 0x100):((page + 1) * 0x100)] = [int(x) for x in self.recv()]

    def open_communication(self, serial_port):
        print('Contacting debugger...')
        self.ser = serial.Serial(serial_port, 115200)
        time.sleep(1)
        self.ack()


##############
#            #
#     UI     #
#            #
##############

class MemoryScreen:

    page = 0x20

    def __init__(self, rows, cols):
        self.window = curses.newwin(rows - 1, cols, 1, 0)

    def update_page(self):
        debugger.update_memory_page(self.page)

    def draw(self):
        self.window.bkgd(curses.color_pair(1), curses.A_BOLD)
        for i in range(0, 16):
            addr = (self.page * 0x100) + (i * 0x10)
            self.window.addstr(i + 2, 4, '{:04X}  :'.format(addr))
            for j in range(0, 16):
                x = 13 + (j * 3) + (0 if j < 8 else 1)
                self.window.addstr(i + 2, x, '{:02X}'.format(debugger.memory[addr + j]))
        rows, cols = self.window.getmaxyx()
        stdscr.chgat(rows, 0, -1, curses.color_pair(2))
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(rows, 0, ' [PgUp] Previous page     [PgDown] Next Page')
        self.window.refresh()

    def key(self, c):
        if c == 'KEY_PPAGE' or c == 'KEY_UP':
            self.page -= 1
            if self.page < 0:
                self.page = 255
            self.update_page()
            self.draw()
        elif c == 'KEY_NPAGE' or c == 'KEY_DOWN':
            self.page += 1
            if self.page > 255:
                self.page = 0
            self.update_page()
            self.draw()


class CodeScreen:

    top = 0

    def __init__(self, rows, cols):
        self.window = curses.newwin(rows - 1, cols, 1, 0)

    def adjust_top(self, pc_visible):
        rows, cols = self.window.getmaxyx()
        if pc_visible and debugger.pc in debugger.source_map_pc:
            pc_line = debugger.source_map_pc[debugger.pc]
            if pc_line < self.top or pc_line >= (self.top + rows) - 1:
                self.top = pc_line - 3
        if self.top < 0:
            self.top = 0
        if self.top >= len(debugger.source) - 2:
            self.top = len(debugger.source) - 2

    def draw(self, pc_visible=True):
        rows, cols = self.window.getmaxyx()
        self.window.bkgd(curses.color_pair(1), curses.A_BOLD)
        self.window.clear()
        self.adjust_top(pc_visible)
        y = 0
        for i in range(self.top, self.top + rows):
            try:
                if i in debugger.source_map and debugger.source_map[i] == debugger.pc:
                    self.window.attron(curses.color_pair(3))
                    self.window.chgat(i - self.top, 0, -1, curses.color_pair(3))
                self.window.addstr(y, 0, debugger.source[i])
                self.window.attroff(curses.color_pair(3))
                y += 1
            except:
                pass
        stdscr.chgat(rows, 0, -1, curses.color_pair(2))
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(rows, 0, ' [S] Step   [R] Reset')
        self.window.refresh()

    def key(self, c):
        if c == 'S' or c == 's':
            debugger.next()
            self.draw()
        elif c == 'R' or c == 'r':
            debugger.reset()
            self.draw()
        elif c == 'KEY_DOWN':
            self.top += 1
            self.draw(False)
        elif c == 'KEY_UP':
            self.top -= 1
            self.draw(False)


class MainScreen:

    selected = 'code'

    def __init__(self):
        rows, cols = stdscr.getmaxyx()
        self.memory = MemoryScreen(rows, cols)
        self.code = CodeScreen(rows, cols)

    def initial_draw(self):
        stdscr.bkgd(curses.color_pair(1), curses.A_BOLD)
        stdscr.clear()
        stdscr.chgat(0, 0, -1, curses.color_pair(2))
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(' [F1] Code     [F2] Memory      [F10] Quit')
        stdscr.refresh()
        self.draw()

    def draw(self):
        if self.selected == 'memory':
            self.memory.draw()
        elif self.selected == 'code':
            self.code.draw()

    def key(self, c):
        if c == curses.KEY_F1 or c == 'KEY_F(1)' or c == '1':
            curses.curs_set(0)
            self.selected = 'code'
            self.initial_draw()
        elif c == curses.KEY_F2 or c == 'KEY_F(2)' or c == '2':
            curses.curs_set(0)
            self.selected = 'memory'
            self.memory.update_page()
            self.initial_draw()
        elif self.selected == 'memory':
            self.memory.key(c)
        elif self.selected == 'code':
            self.code.key(c)


def run_ui(stdscr):
    curses.noecho()
    curses.cbreak()
    curses.curs_set(0)
    stdscr.keypad(True)

    curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)

    main_screen = MainScreen()
    main_screen.initial_draw()

    while True:
        c = stdscr.getkey()
        if c == curses.KEY_F10 or c == '0' or c == 'q':
            break
        else:
            main_screen.key(c)


##############
#            #
#    MAIN    #
#            #
##############

if len(sys.argv) != 3:
    print('Usage: %s SERIAL_PORT SOURCE' % sys.argv[0])
    sys.exit(1)

dbg_source, rom = compile_source(sys.argv[2])

debugger = Debugger()
debugger.open_communication(sys.argv[1])
print("Uploading ROM...")
debugger.update_source(dbg_source)
debugger.upload_rom(rom)
del rom

debugger.reset()

stdscr = curses.initscr()
curses.start_color()
wrapper(run_ui)
