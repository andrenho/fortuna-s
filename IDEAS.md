# Version 1

Base board:
- Power input + power led
- Z80 running at 6 Mhz (?)
  - reset button
  - clock generator
- ROM memory (8 kB)
- RAM memory (56 kB) - use 512 kB IC, possibly expandable?
- SD card + LED
- UART IC
  - 8251 16550 16450 Z80SIO ?
  - FTDI + direct serial
- Expander pins

Debugger board

ROM = BIOS, includes:
- Boot code
- SPI code
- SD code
- FAT code (?)
