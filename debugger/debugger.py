#!/usr/bin/env python3

import argparse
import curses
from curses import wrapper
import logging
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

CALL_OPS = [0xC4, 0xCC, 0xCD, 0xD4, 0xDC, 0xE4, 0xEC, 0xF4, 0xFC]
RST_OPS = [0xC7, 0xCF, 0xD7, 0xDF, 0xE7, 0xEF, 0xF7, 0xFF]

class CommunicationException(Exception):
    pass

class Debugger:
    memory = [0xff for _ in range(64 * 1024)]
    pc = 0
    registers = []
    source = []
    source_map = {}
    source_map_pc = {}
    dbg_source = None
    rom = None
    breakpoints = []

    def __init__(self, log=False):
        self.reset_registers()
        logging.basicConfig(filename='debugger.log', encoding='utf-8', level=logging.DEBUG if log else logging.INFO)

    def reset_registers(self):
        self.registers = [None] * 16

    def open_communication(self, serial_port):
        print('Contacting debugger...')
        self.ser = serial.Serial(serial_port, 115200)
        time.sleep(1)
        self.ack()

    def initialize(self, dbg_source=None, rom=None, clear_rom=False):
        stdscr.clear()
        debugger.update_source(dbg_source or self.dbg_source)
        if clear_rom:
            stdscr.addstr("Clearing ROM...")
            stdscr.refresh()
            self.clear_rom()
            stdscr.addstr("\n")
        stdscr.addstr("Uploading ROM...")
        stdscr.refresh()
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
        logging.debug("> " + cmd)
        self.ser.write(bytes(cmd + '\n', 'latin1'))

    def recv(self):
        b = self.ser.readline().decode('latin1').replace('\n', '').replace('\r', '').split()
        logging.debug("< " + repr(b))
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
        self.reset_registers()

    def next_dbg(self):
        self.send('N')
        regs = [int(x) for x in self.recv()]
        self.registers = regs
        self.pc = regs[11]

    def next_over(self):
        sz = self.jump_instruction_sz()
        if sz:
            bkp = self.pc + sz
            if bkp not in self.breakpoints:
                self.swap_breakpoint(bkp)
            self.run()
            self.swap_breakpoint(bkp)
        else:
            self.next_dbg()

    def run(self):
        self.send('x')
        self.pc = int(self.recv()[0])
        self.reset_registers()

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

    def clear_rom(self):
        for i in range(0, 0x2000, 16):
            request = ('w %d 16 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0' % i)
            self.send(request)
            self.recv()
            stdscr.addch('.')
            stdscr.refresh()
        stdscr.addstr("\n")

    # if the next instruction is a jump, returns instruction size, or None otherwise
    def jump_instruction_sz(self):
        self.send('r %d 1' % self.pc)
        opc = int(self.recv()[0])
        if opc in CALL_OPS:
            return 3
        elif opc in RST_OPS:
            return 1
        else:
            return None  # not a call

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
            self.window.addstr(i + 2, 1, '{:04X}  :'.format(addr))
            for j in range(0, 16):
                x = 10 + (j * 3) + (0 if j < 8 else 1)
                data = debugger.memory[addr + j]
                self.window.addstr(i + 2, x, '{:02X}'.format(data))
                self.window.addch(i + 2, 62 + j, chr(data) if data >= 32 and data < 127 else '.')
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
            if pc_line < self.top or pc_line >= (self.top + rows) - 5:
                self.top = pc_line - 3
        if self.top < 0:
            self.top = 0
        if self.top >= len(debugger.source) - 2:
            self.top = len(debugger.source) - 2

    def print_registers(self):
        rows, cols = self.window.getmaxyx()
        self.window.move(rows - 3, 0)
        self.window.clrtoeol()
        self.window.chgat(rows - 3, 0, -1, curses.color_pair(5))
        self.window.attron(curses.color_pair(5))
        def reg(s, i):
            return s.replace("{}", ("%04X" % debugger.registers[i]) if debugger.registers[i] != None else "????")
        self.window.addstr(reg("AF:{} ", 0))
        self.window.addstr(reg("BC:{} ", 1))
        self.window.addstr(reg("DE:{} ", 2))
        self.window.addstr(reg("HL:{} ", 3))
        self.window.addstr(reg("IX:{} ", 4))
        self.window.addstr(reg("IY:{} ", 5))
        self.window.addstr(reg("SP:{} ", 10))
        self.window.addstr(reg("PC:{} ", 11))
        self.window.addstr("FL:")
        if debugger.registers[0]:
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
        else:
            self.window.addstr("???")

        self.window.move(rows - 2, 0)
        self.window.clrtoeol()
        self.window.chgat(rows - 2, 0, -1, curses.color_pair(5))
        self.window.addstr("Stack: PUSH-> ")
        for i in range(12, 16):
            self.window.addstr(reg("{} ", i))
        self.window.addstr(reg("  AF':{} ", 6))
        self.window.addstr(reg("BC':{} ", 7))
        self.window.addstr(reg("DE':{} ", 8))
        self.window.addstr(reg("HL':{} ", 9))
        self.window.attroff(curses.color_pair(5))

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
                line = replace_tabs_with_spaces(debugger.source[i])[0:cols]
                if i in debugger.source_map and debugger.source_map[i] == debugger.pc:
                    self.window.attron(curses.color_pair(3))
                    self.window.chgat(i - self.top, 0, -1, curses.color_pair(3))
                    self.window.addstr(y, 0, line)
                    self.window.attroff(curses.color_pair(3))
                elif i in debugger.source_map and debugger.source_map[i] in debugger.breakpoints:
                    self.window.attron(curses.color_pair(4))
                    self.window.chgat(i - self.top, 0, -1, curses.color_pair(4))
                    self.window.addstr(y, 0, line)
                    self.window.attroff(curses.color_pair(4))
                else:
                    self.window.addstr(y, 0, line)
                    comment_pos = line.find(';')
                    if comment_pos > 0:
                        self.window.chgat(y, comment_pos, -1, curses.color_pair(7))
                    self.window.chgat(y, 0, 40, curses.color_pair(6))
                y += 1
            except (curses.error, IndexError):
                pass
        
        # write register bar
        self.print_registers()
        
        # write status bar
        stdscr.chgat(rows, 0, -1, curses.color_pair(2))
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(rows, 0, '[S] Step  [N] Next  [R] Reload  [B] Bkp  [X] Clear bkps  [C] Run')

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

    def run(self):
        self.draw_running()
        debugger.run()
        self.draw()

    def key(self, c):
        if c == 'S' or c == 's':
            debugger.next_dbg()
            self.draw()
        elif c == 'C' or c == 'c':
            self.run()
        elif c == 'N' or c == 'n':
            debugger.next_over()
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

    bg = curses.COLOR_BLACK

    curses.init_pair(1, curses.COLOR_WHITE, bg)   # general text
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)   # menus
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLUE)    # current pc
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_RED)     # breakponts
    curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_MAGENTA) # register line
    curses.init_pair(6, curses.COLOR_CYAN, bg)     # line indicators
    curses.init_pair(7, curses.COLOR_YELLOW, bg)    # comments

    main_screen = MainScreen()
    main_screen.initial_draw()

    if args.run:
        main_screen.code.run()

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

parser = argparse.ArgumentParser()
parser.add_argument('source')
parser.add_argument('-p', '--serial-port', required=True)
parser.add_argument('-r', '--run', action='store_true')
parser.add_argument('-l', '--log', action='store_true')
parser.add_argument('-c', '--clear-rom', action='store_true')
args = parser.parse_args()

dbg_source, rom = compile_source(args.source)

debugger = Debugger(args.log)
debugger.open_communication(args.serial_port)

stdscr = curses.initscr()
curses.start_color()

debugger.initialize(dbg_source, rom, args.clear_rom)
del rom

wrapper(run_ui)
