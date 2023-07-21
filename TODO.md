# Version A - basic computer

### Hardware

- [x] Z80
- [x] ROM + RAM
- [x] UART
- [x] Power + Reset
- [ ] Expansion pins

### Debugger (hardware + firmware)

- [x] Debugger hardware
- [x] Memory functions
- [x] Z80 functions
- [x] Prepare for connection with debugger (software)
- [x] Emulate UART (output)
- [x] Emulate UART (input)
- [x] Interrupt

### Debugger (software)

- [x] Basic project
- [x] Show ROM/RAM
- [x] Upload ROM
- [x] Load project
- [x] Debug (basic)
- [x] Emulate UART (output)
- [x] Emulate UART (input)

---

# Version B - improved debugger

### Debugger (software)

- [x] Add breakpoints
- [x] Run until breakpoint
- [x] Show registers
- [x] Show stack
- [x] Code formatting
- [x] Next
- [ ] Search function

### Debugger (firmware)
- [x] NMI (for getting registers)

### Z80 software

- [x] NMI (interrupt that gets registers)

### Z80 software

- [x] Monitor
- [x] Serial (syscall)
- [x] Bankswitching (syscall)

--

# Version C - SD Card

### Hardware

- [ ] Create hardware for SDCard

### Filesystem

- [ ] Design filesystem
- [ ] Create FUSE library to manage filesystem

### Z80 software

- [ ] SDCard management
- [ ] Filesystem support

---

# Version D - CP/M

### Hardware

- [ ] Create I/O port to swap between ROM and RAM

### Software

- [ ] Port CP/M
  - [ ] Write BIOS

---

# Version E - video

---
