typedef enum {
  D0 = 16, D1 = 18, D2 = 12, D3 = 4, D4 = 2, D5 = 6, D6 = 8, D7 = 14,
  A0_ = 65, A1_ = 63, A2_ = 61, A3_ = 59, A4_ = 57, A5_ = 55, A6_ = 54, A7_ = 56,
  A8_ = 58, A9_ = 60, A10_ = 62, A11_ = 10, A12_ = 11, A13_ = 9, A14_ = 7, A15_ = 5,
  A16_ = 24, A17_ = 69, A18_ = 39,
  INT = 20, CLK = 3, NMI = 22, MREQ = 26, IORQ = 28, M1 = 33, RST = 35, BUSRQ = 37,
  BUSAK = 41, WR = 43, RD = 45, ROM_WE = 47,
} Pin;

// uncomment next define to debug Z80 states between cycles
#define PRINT_STATE() //   printState()

#define N_BKPS 16
int breakpoints[N_BKPS] = { -1 };

void swap_breakpoint(int bkp)
{
  for (int i = 0; i < N_BKPS; ++i) {
    if (breakpoints[i] == bkp) {
      breakpoints[i] = -1;
      return;
    }
  }
  for (int i = 0; i < N_BKPS; ++i) {
    if (breakpoints[i] == -1) {
      breakpoints[i] = bkp;
      return;
    }
  }
}

class AddressBus {
public:

  static void setBusControl(bool control) {
    auto mode = control ? OUTPUT : INPUT;
    pinMode(A0_, mode);
    pinMode(A1_, mode);
    pinMode(A2_, mode);
    pinMode(A3_, mode);
    pinMode(A4_, mode);
    pinMode(A5_, mode);
    pinMode(A6_, mode);
    pinMode(A7_, mode);
    pinMode(A8_, mode);
    pinMode(A9_, mode);
    pinMode(A10_, mode);
    pinMode(A11_, mode);
    pinMode(A12_, mode);
    pinMode(A13_, mode);
    pinMode(A14_, mode);
    pinMode(A15_, mode);
  }

  static uint32_t getAddress() {
    setBusControl(false);
    uint32_t addr = 0x0;
    addr |= (digitalRead(A0_) == HIGH ? (1 << 0) : 0);
    addr |= (digitalRead(A1_) == HIGH ? (1U << 1) : 0);
    addr |= (digitalRead(A2_) == HIGH ? (1U << 2) : 0);
    addr |= (digitalRead(A3_) == HIGH ? (1U << 3) : 0);
    addr |= (digitalRead(A4_) == HIGH ? (1U << 4) : 0);
    addr |= (digitalRead(A5_) == HIGH ? (1U << 5) : 0);
    addr |= (digitalRead(A6_) == HIGH ? (1U << 6) : 0);
    addr |= (digitalRead(A7_) == HIGH ? (1U << 7) : 0);
    addr |= (digitalRead(A8_) == HIGH ? (1U << 8) : 0);
    addr |= (digitalRead(A9_) == HIGH ? (1U << 9) : 0);
    addr |= (digitalRead(A10_) == HIGH ? (1U << 10) : 0);
    addr |= (digitalRead(A11_) == HIGH ? (1U << 11) : 0);
    addr |= (digitalRead(A12_) == HIGH ? (1U << 12) : 0);
    addr |= (digitalRead(A13_) == HIGH ? (1U << 13) : 0);
    addr |= (digitalRead(A14_) == HIGH ? (1U << 14) : 0);
    addr |= (digitalRead(A15_) == HIGH ? (1U << 15) : 0);
    return addr;
  }

  static void setAddress(uint32_t addr) {
    setBusControl(true);
    digitalWrite(A0_, (addr & (1 << 0)) != 0 ? HIGH : LOW);
    digitalWrite(A1_, (addr & (1 << 1)) != 0 ? HIGH : LOW);
    digitalWrite(A2_, (addr & (1 << 2)) != 0 ? HIGH : LOW);
    digitalWrite(A3_, (addr & (1 << 3)) != 0 ? HIGH : LOW);
    digitalWrite(A4_, (addr & (1 << 4)) != 0 ? HIGH : LOW);
    digitalWrite(A5_, (addr & (1 << 5)) != 0 ? HIGH : LOW);
    digitalWrite(A6_, (addr & (1 << 6)) != 0 ? HIGH : LOW);
    digitalWrite(A7_, (addr & (1 << 7)) != 0 ? HIGH : LOW);
    digitalWrite(A8_, (addr & (1 << 8)) != 0 ? HIGH : LOW);
    digitalWrite(A9_, (addr & (1 << 9)) != 0 ? HIGH : LOW);
    digitalWrite(A10_, (addr & (1 << 10)) != 0 ? HIGH : LOW);
    digitalWrite(A11_, (addr & (1 << 11)) != 0 ? HIGH : LOW);
    digitalWrite(A12_, (addr & (1 << 12)) != 0 ? HIGH : LOW);
    digitalWrite(A13_, (addr & (1 << 13)) != 0 ? HIGH : LOW);
    digitalWrite(A14_, (addr & (1 << 14)) != 0 ? HIGH : LOW);
    digitalWrite(A15_, (addr & (1 << 15)) != 0 ? HIGH : LOW);
  }

};

class DataBus {
public:

  static void setBusControl(bool control) {
    auto mode = control ? OUTPUT : INPUT;
    pinMode(D0, mode);
    pinMode(D1, mode);
    pinMode(D2, mode);
    pinMode(D3, mode);
    pinMode(D4, mode);
    pinMode(D5, mode);
    pinMode(D6, mode);
    pinMode(D7, mode);
  }

  static uint8_t getData() {
    setBusControl(false);
    uint8_t data = 0x0;
    data |= (digitalRead(D0) == HIGH ? (1U << 0) : 0);
    data |= (digitalRead(D1) == HIGH ? (1U << 1) : 0);
    data |= (digitalRead(D2) == HIGH ? (1U << 2) : 0);
    data |= (digitalRead(D3) == HIGH ? (1U << 3) : 0);
    data |= (digitalRead(D4) == HIGH ? (1U << 4) : 0);
    data |= (digitalRead(D5) == HIGH ? (1U << 5) : 0);
    data |= (digitalRead(D6) == HIGH ? (1U << 6) : 0);
    data |= (digitalRead(D7) == HIGH ? (1U << 7) : 0);
    return data;
  }

  static void setData(uint8_t data) {
    setBusControl(true);
    digitalWrite(D0, (data & (1 << 0)) != 0 ? HIGH : LOW);
    digitalWrite(D1, (data & (1 << 1)) != 0 ? HIGH : LOW);
    digitalWrite(D2, (data & (1 << 2)) != 0 ? HIGH : LOW);
    digitalWrite(D3, (data & (1 << 3)) != 0 ? HIGH : LOW);
    digitalWrite(D4, (data & (1 << 4)) != 0 ? HIGH : LOW);
    digitalWrite(D5, (data & (1 << 5)) != 0 ? HIGH : LOW);
    digitalWrite(D6, (data & (1 << 6)) != 0 ? HIGH : LOW);
    digitalWrite(D7, (data & (1 << 7)) != 0 ? HIGH : LOW);
  }

};

class Memory {
public:

  static void initialize() {
    pinMode(ROM_WE, OUTPUT);
    digitalWrite(ROM_WE, HIGH);
  }

  static uint8_t read(uint32_t addr) {
    AddressBus::setAddress(addr);
    pinMode(RD, OUTPUT);
    pinMode(MREQ, OUTPUT);
    digitalWrite(RD, LOW);
    digitalWrite(MREQ, LOW);
    delayMicroseconds(10);
    uint8_t data = DataBus::getData();
    // for (;;);
    pinMode(RD, INPUT_PULLUP);
    pinMode(MREQ, INPUT_PULLUP);
    AddressBus::setBusControl(false);
    return data;
  }

  static bool write(uint32_t addr, uint8_t data) {
    auto wrPin = (addr < 0x2000) ? ROM_WE : WR;
    AddressBus::setAddress(addr);
    DataBus::setData(data);
    pinMode(wrPin, OUTPUT);
    pinMode(MREQ, OUTPUT);
    digitalWrite(wrPin, LOW);
    digitalWrite(MREQ, LOW);
    delayMicroseconds(100);
    pinMode(wrPin, INPUT_PULLUP);
    pinMode(MREQ, INPUT_PULLUP);
    delayMicroseconds(100);

    if (data != 0)
      DataBus::setData(0);
    else
      DataBus::setData(0xff);

    for (size_t i = 0; i < 1000; ++i) {
      if (read(addr) == data)
        return true;
      delayMicroseconds(100);
    }

    return false;
  }

};



class Z80 {
public:

  static int regs[12];

  static void initialize() {
    pinMode(CLK, OUTPUT);
    pinMode(RST, OUTPUT);
    pinMode(BUSRQ, OUTPUT);
    pinMode(NMI, OUTPUT);

    digitalWrite(RST, LOW);
    digitalWrite(BUSRQ, HIGH);
    digitalWrite(NMI, HIGH);

    pinMode(RD, INPUT_PULLUP);
    pinMode(MREQ, INPUT_PULLUP);
    pinMode(ROM_WE, INPUT_PULLUP);
    pinMode(WR, INPUT_PULLUP);

    cycle();
  }

  static bool isBusFree() {
    return digitalRead(RST) == LOW || digitalRead(BUSAK) == LOW;
  }

  static void cycle() {
    digitalWrite(CLK, HIGH);
    digitalWrite(CLK, LOW);
  }

  static void next_debug() {
    digitalWrite(NMI, LOW);
    cycle();
    digitalWrite(NMI, HIGH);
    for (int i = 0; i < 22 + 3 ; ++i)
      next();
    takeOverBus();
    for (int i = 0; i < 11; ++i)
      regs[i] = ((uint16_t) Memory::read(0x2000 + i) << 8) | Memory::read(0x2000 + i + 1);
    releaseBus();
    next();
    regs[11] = AddressBus::getAddress();
  }

  static void next() {
    digitalWrite(BUSRQ, HIGH);  // make sure we're not requesting the bus
    cycle();
    PRINT_STATE();

    // TODO - what if it's a two-byte opcode?
    while (digitalRead(M1) != LOW) {   // run until we receive a M1 from the Z80
      cycle();
      PRINT_STATE();
    }
    
    cycle();
    PRINT_STATE();

    // skip combined instructions
    static uint8_t previous_instruction = 0x00;
    bool combined_instruction = (previous_instruction == 0xcb || previous_instruction == 0xdd || previous_instruction == 0xed || previous_instruction == 0xfd);
    previous_instruction = DataBus::getData();
    if (combined_instruction)
      next();
  }

  static void interrupt() {
    pinMode(INT, OUTPUT);
    digitalWrite(INT, LOW);
    cycle();
    PRINT_STATE();
    cycle();
    PRINT_STATE();  
    digitalWrite(INT, HIGH);
    pinMode(INT, HIGH);
  }

  static void reset() {
    digitalWrite(RST, LOW);
    for (size_t i = 0; i < 50; ++i) 
      cycle();
    digitalWrite(RST, HIGH);
    PRINT_STATE();
  }

  static void releaseBus() {
    if (digitalRead(RST) == HIGH) {
      digitalWrite(BUSRQ, LOW);
      while (digitalRead(BUSAK) != LOW) {
        cycle();
        PRINT_STATE();
      }
    }
  }

  static void takeOverBus() {
    if (digitalRead(RST) == HIGH) {
      digitalWrite(BUSRQ, HIGH);
      while (digitalRead(BUSAK) != HIGH) {
        cycle();
        PRINT_STATE();
      }
    }
  }

  static void printState() {
    if (digitalRead(IORQ) == LOW)
      Serial.print(AddressBus::getAddress() & 0x80, HEX);
    else if (digitalRead(MREQ) == LOW)
      Serial.print(AddressBus::getAddress(), HEX);
    else
      Serial.print('?');
    Serial.print(' ');
    if (digitalRead(MREQ) == LOW || digitalRead(IORQ) == LOW)
      Serial.print(DataBus::getData(), HEX);
    else
      Serial.print('?');
    Serial.print(" : ");
    Serial.print(digitalRead(M1) == LOW ? "M1 " : "");
    Serial.print(digitalRead(MREQ) == LOW ? "MREQ " : "");
    Serial.print(digitalRead(WR) == LOW ? "WR " : "");
    Serial.print(digitalRead(RD) == LOW ? "RD " : "");
    Serial.print(digitalRead(BUSAK) == LOW ? "BUSAK " : "");
    Serial.print(digitalRead(IORQ) == LOW ? "IORQ " : "");
    Serial.print(digitalRead(INT) == LOW ? "INT " : "");
    Serial.println();
  }

};

int Z80::regs[12] = { 0 };

void setup() {
  Serial.begin(115200);
  Z80::initialize();
  Memory::initialize();
  for (int i = 0; i < N_BKPS; ++i)
          breakpoints[i] = -1;
}

void loop() {
  if (Serial.available() > 0) {

    char c = Serial.read();
start:
    switch (c) {

      case 'h':  // acknowledgement
        Serial.println('+');
        break;

      case 'r': {  // read byte from memory position
        uint32_t addr = Serial.parseInt();
        int count = Serial.parseInt();
        Z80::releaseBus();
        for (int i = 0; i < count; ++i) {
          Serial.print(Memory::read(addr + i));
          Serial.print(' ');
        }
        Serial.println();
        break;
      }

      case 'w': {   // write byte to memory position
        uint32_t addr = Serial.parseInt();
        int count = Serial.parseInt();
        Serial.setTimeout(10000);
        Z80::releaseBus();
        bool success = true;
        for (int i = 0; i < count; ++i) {
          uint8_t data = Serial.parseInt();
          if (!Memory::write(addr + i, data))
            success = false;
        }
        Serial.println(success ? '+' : 'x');
        Serial.setTimeout(1000);
        break;
      }

      case 'R':  // reset Z80
        Z80::reset();
        Serial.println('+');
        break;

      case 's':   // Z80 single step cycle
        Z80::cycle();
        Z80::printState();
        break;

      case 'n':   // Z80 run until next instruction
        Z80::next();
        Serial.println(AddressBus::getAddress());
        break;

      case 'x':   // run
        while (true) {
          if (Serial.available() > 0) {
            c = Serial.read();
            if (c != 10 && c != 13)
              goto start;
          }
          Z80::next();
          int pc = AddressBus::getAddress();
          // Serial.println(pc);
          for (int i = 0; i < N_BKPS; ++i)
            if (breakpoints[i] == pc)
              goto breakpoint;
        }
breakpoint:
        Serial.println(AddressBus::getAddress());
        break;

      case 'N':  // next with debugging information
        Z80::next_debug();
        for (int i = 0; i < 12; ++i) {
          Serial.print(Z80::regs[i]);
          Serial.print(' ');
        }
        Serial.println();
        break;

      case 'b':   // request Z80 bus
        Z80::releaseBus();
        Serial.println('+');
        break;

      case 'B':   // make Z80 take over bus
        Z80::takeOverBus();
        Serial.println('+');
        break;

      case 'k':   // swap breakpoint
        swap_breakpoint(Serial.parseInt());
        for (int i = 0; i < N_BKPS; ++i) {
          Serial.print(breakpoints[i]);
          Serial.print(' ');          
        }
        Serial.println();
        break;

      case 'c':   // clear breakpoints
        for (int i = 0; i < N_BKPS; ++i)
          breakpoints[i] = -1;
        Serial.println('+');
        break;

      case '?':   // request Z80 state
        Z80::printState();
        break;

      case 'f':  // is bus free?
        if (Z80::isBusFree())
          Serial.println('y');
        else
          Serial.println('n');
        break;
      
      case 10:  // ignore line breaks
      case 13:
        break;
      
      default:  // command not recognized
        Serial.println('x');
    }
  }
}
