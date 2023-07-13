#!/usr/bin/env python3

import curses
from curses import wrapper
import os
import platform
import random
import re
import serial
import subprocess
import time
import sys

def replace_tabs_with_spaces(text, tab_width=8):
    result = ""
    for char in text:
        if char == '\t':
            # Calculate the number of spaces needed to reach the next tab stop
            spaces = tab_width - (len(result) % tab_width)
            result += " " * spaces
        else:
            result += char
    return result


##############
#            #
#  Compiler  #
#            #
##############

def compile_source(source_filename):
    exe = './vasmz80_oldstyle'
    if platform.system() == 'Windows':
        exe += '.exe'
    cp = subprocess.run([exe, '-chklabels', '-L', 'listing.txt', '-Llo', '-Lns', '-ignore-mult-inc', '-nosym', '-x', '-Fbin', '-o', 'rom.bin', source_filename], capture_output=True, text=True)
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
    registers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    source = []
    source_map = {}
    source_map_pc = {}
    dbg_source = None
    rom = None
    breakpoints = []

    def open_communication(self, serial_port):
        print('Contacting debugger...')
        self.ser = serial.Serial(serial_port, 115200)
        time.sleep(1)
        self.ack()

    def initialize(self, dbg_source=None, rom=None):
        stdscr.clear()
        stdscr.addstr("Uploading ROM...")
        stdscr.refresh()
        debugger.update_source(dbg_source or self.dbg_source)
        debugger.upload_rom(rom or self.rom)
        debugger.reset()
        if dbg_source:
            self.dbg_source = dbg_source
        if rom:
            self.rom = rom

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
        self.registers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    def next_dbg(self):
        self.send('N')
        regs = [int(x) for x in self.recv()]
        self.registers = regs
        self.pc = regs[11]

    def run(self):
        self.send('x')
        self.pc = int(self.recv()[0])

    def swap_breakpoint(self, bkp):
        self.send('k %d' % bkp)
        self.breakpoints = []
        for s in self.recv():
            addr = int(s)
            if addr != -1:
                self.breakpoints.append(addr)

    def clear_breakpoints(self):
        self.send('c')
        self.recv()
        self.breakpoints = []

    def emulate_keypress(self, key):
        self.send('U %d' % (key & 0xff))

    def upload_rom(self, rom):
        for i in range(0, len(rom), 16):
            bts = rom[i:(i+16)]
            request = ('w %d %d ' % (i, len(bts))) + ' '.join([str(x) for x in bts])
            self.send(request)
            self.recv()
            stdscr.addch('.')
            stdscr.refresh()
        stdscr.addstr("\n")

    def update_memory_page(self, page):
        self.send('r %d 256' % (page * 0x100))
        self.memory[(page * 0x100):((page + 1) * 0x100)] = [int(x) for x in self.recv()]


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
                data = debugger.memory[addr + j]
                self.window.addstr(i + 2, x, '{:02X}'.format(data))
                self.window.addch(i + 2, 67 + j, chr(data) if data >= 32 and data < 127 else '.')
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

    def print_registers(self):
        self.window.addstr("A:%02X " % (debugger.registers[0] >> 8))
        self.window.addstr("BC:%04X " % (debugger.registers[1] & 0xffff))
        self.window.addstr("DE:%04X " % (debugger.registers[2] & 0xffff))
        self.window.addstr("HL:%04X " % (debugger.registers[3] & 0xffff))
        self.window.addstr("IX:%04X " % (debugger.registers[4] & 0xffff))
        self.window.addstr("IY:%04X " % (debugger.registers[5] & 0xffff))
        self.window.addstr("SP:%04X " % (debugger.registers[10] & 0xffff))
        self.window.addstr("PC:%04X " % (debugger.registers[11] & 0xffff))
        self.window.addstr("AF':%04X " % (debugger.registers[6] & 0xffff))
        self.window.addstr("BC':%04X " % (debugger.registers[7] & 0xffff))
        self.window.addstr("DE':%04X " % (debugger.registers[8] & 0xffff))
        self.window.addstr("HL':%04X " % (debugger.registers[9] & 0xffff))
        self.window.addstr("FL:")
        flags = debugger.registers[0] & 0xff
        if flags & (1 << 0):
            self.window.addstr("C")
        if flags & (1 << 1):
            self.window.addstr("N")
        if flags & (1 << 2):
            self.window.addstr("P")
        if flags & (1 << 4):
            self.window.addstr("H")
        if flags & (1 << 6):
            self.window.addstr("Z")
        if flags & (1 << 7):
            self.window.addstr("S")

    def draw(self, pc_visible=True):
        
        # clear screen
        rows, cols = self.window.getmaxyx()
        self.window.bkgd(curses.color_pair(1), curses.A_BOLD)
        self.window.clear()
        self.adjust_top(pc_visible)
        
        # write code
        y = 0
        for i in range(self.top, self.top + rows):
            try:
                if i in debugger.source_map and debugger.source_map[i] == debugger.pc:
                    self.window.attron(curses.color_pair(3))
                    self.window.chgat(i - self.top, 0, -1, curses.color_pair(3))
                    self.window.addstr(y, 0, debugger.source[i])
                    self.window.attroff(curses.color_pair(3))
                elif i in debugger.source_map and debugger.source_map[i] in debugger.breakpoints:
                    self.window.attron(curses.color_pair(4))
                    self.window.chgat(i - self.top, 0, -1, curses.color_pair(4))
                    self.window.addstr(y, 0, debugger.source[i])
                    self.window.attroff(curses.color_pair(4))
                else:
                    line = replace_tabs_with_spaces(debugger.source[i])
                    self.window.addstr(y, 0, line)
                    comment_pos = line.find(';')
                    if comment_pos > 0:
                        self.window.chgat(y, comment_pos, -1, curses.color_pair(7))
                    self.window.chgat(y, 0, 40, curses.color_pair(6))
                y += 1
            except (curses.error, IndexError):
                pass
        
        # write register bar
        self.window.move(rows - 2, 0)
        self.window.clrtoeol()
        self.window.chgat(rows - 2, 0, -1, curses.color_pair(5))
        self.window.attron(curses.color_pair(5))
        self.print_registers()
        self.window.attroff(curses.color_pair(5))
        
        # write status bar
        stdscr.chgat(rows, 0, -1, curses.color_pair(2))
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(rows, 0, '[S] Step  [R] Reload  [B] Bkp  [X] Clear bkps  [C] Run')

        # refresh
        self.window.refresh()

    def draw_running(self):
        rows, cols = self.window.getmaxyx()
        self.window.bkgd(curses.color_pair(1), curses.A_BOLD)
        self.window.clear()
        self.window.addstr(1, 2, "Running...")
        self.window.refresh()

    def ask_for_breakpoint(self):
        rows, cols = self.window.getmaxyx()
        self.window.attron(curses.color_pair(4))
        self.window.addstr(rows - 1, 57, " Bkp addr (hex):      ")
        self.window.move(rows - 1, 74)
        curses.curs_set(1)
        curses.echo()
        self.window.refresh()
        try:
            bkp_s = self.window.getstr(4).decode()
            bkp = int(bkp_s, 16)
            debugger.swap_breakpoint(bkp)
        except TypeError:
            pass
        self.window.attroff(curses.color_pair(4))
        curses.noecho()
        curses.curs_set(0)

    def key(self, c):
        if c == 'S' or c == 's':
            debugger.next_dbg()
            self.draw()
        elif c == 'C' or c == 'c':
            self.draw_running()
            debugger.run()
            self.draw()
        elif c == 'X' or c == 'x':
            debugger.clear_breakpoints()
            self.draw()
        elif c == 'B' or c == 'b':
            self.ask_for_breakpoint()
            self.draw()
        elif c == 'KEY_DOWN':
            self.top += 1
            self.draw(False)
        elif c == 'KEY_UP':
            self.top -= 1
            self.draw(False)
        elif c == 'KEY_PPAGE' or c == 'KEY_UP':
            self.top -= 24
            self.draw(False)
        elif c == 'KEY_NPAGE' or c == 'KEY_DOWN':
            self.top += 24
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
        elif c == 'R' or c == 'r':
            debugger.initialize()
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

    curses.init_pair(1, curses.COLOR_WITE, curses.COLOR_BLACK)   # general text
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)   # menus
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_CYAN)    # current pc
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)     # breakponts
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # register line
    curses.init_pair(6, curses.COLOR_CYAN, curses.COLOR_BLACK)     # line indicators
    curses.init_pair(7, curses.COLOR_YELLOW, curses.COLOR_BLACK)    # comments

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

stdscr = curses.initscr()
curses.start_color()

debugger.initialize(dbg_source, rom)
del rom

wrapper(run_ui)
