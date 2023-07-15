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
0000-1FFF   BIOS
  0000-00FF   Interrupt vector
  0100-01FF   DHS (debugger helper subroutine)
  0200-02FF   Initialization code
  0300-05FF   Monitor
2000-FFFF   Bankswitched RAM
  2000-27FF   RAM (reserved for operating system)
    2000-201F   DHS temporary memory
  2800-FFFF   Free for application use
```

## I/O

```
0x80  UART config (MC65B80)
0x81  UART read/write
```

## Monitor

Example commands:

```
2000             Read RAM location 0x2000
2000.20FF        Read RAM locations from 0x2000 to 0x20FF
2000:A8          Set RAM location 0x2000 to 0xA8
2000:A8 F0 42    Set RAM locations from 0x2000 to 0x2002
:42 78 AF B8     Continue setting RAM locations
R 2000           Run program at 0x2000
I 20             I/O read from port 0x20
O 20:A8          I/O read to port 0x20
```
