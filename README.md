# fortuna-s
A simple computer based on a Z80.

## Specification

* Z80 running at 7.37 Mhz
* 8 kB ROM containing BIOS
* 8x56 kB bankswitched RAM (448 kB total)
* 115200 baud UART (using MC65B80)
* SDCard storage
* VGA + USB keyboard terminal
* Additional header for connecting external devices
* Debugger board, when plugged to the computer allows for code debugging

## Memory map

```
0000-1FFF   ROM
2000-FFFF   Bankswitched RAM
  2000-27FF   RAM (reserved for operating system)
  2800-FFFF   Free for application use
```

## I/O

```
0x80  UART config (MC65B80)
0x81  UART read/write
```
