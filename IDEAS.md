# Version 1 - Base board

Base board:
- Power input + power led + on/off switch
  - Maybe power from FTDI?
- Z80 running at 6 Mhz (?)
  - reset button
  - clock generator
- ROM memory (8 kB)
- RAM memory (56 kB) - use 512 kB IC, possibly expandable?
- SD card + LED + auxiliary IC?
- Debugger pinout (the debugger is an AVR + FTDI)
- Expander pins (to the expansion board): `A0~7`, `D0~7`, memory pins, interrupt

Debugger board:
- AVR
- Programmer
- FTDI (?)

The debugger will do the following functions:
- Computer interface via serial
- Run using serial I/O (simulate keyboard and character output)
- Step-by-step execution
- Memory management
- Debug using debugger output (how?)
- ROM writer

ROM = BIOS, includes:
- Boot code
- Monitor (?)
- SPI code
- SD code
- FAT code (?)

# Version 2 - Expansion board

- Keyboard (USB? PS2?)
- VGA (using RPI Pico)
- Sound
- Wi-Fi
