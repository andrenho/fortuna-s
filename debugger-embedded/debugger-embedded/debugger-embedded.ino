typedef enum {
  D0 = 16, D1 = 18, D2 = 12, D3 = 4, D4 = 2, D5 = 6, D6 = 8, D7 = 14,
  A0_ = 65, A1_ = 63, A2_ = 61, A3_ = 59, A4_ = 57, A5_ = 55, A6_ = 54, A7_ = 56,
  A8_ = 58, A9_ = 60, A10_ = 62, A11_ = 10, A12_ = 11, A13_ = 9, A14_ = 7, A15_ = 5,
  A16_ = 24, A17_ = 69, A18_ = 39,
  INT = 20, CLK = 3, NMI = 22, MREQ = 26, IORQ = 28, M1 = 33, RST = 35, BUSRQ = 37,
  BUSAK = 41, WR = 43, RD = 45, ROM_WE = 47,
} Pin;


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

class Z80 {
public:

  static void initialize() {
    pinMode(CLK, OUTPUT);
    pinMode(RST, OUTPUT);
    pinMode(BUSRQ, OUTPUT);
    digitalWrite(RST, LOW);
    digitalWrite(BUSRQ, HIGH);
  }

  static void cycle() {
    digitalWrite(CLK, HIGH);
    digitalWrite(CLK, LOW);
  }

  static void next() {
    cycle();
    printState();
    while (digitalRead(M1) != LOW) {
      cycle();
      printState();
    }
    cycle();
    printState();
  }

  static void reset() {
    digitalWrite(RST, LOW);
    for (size_t i = 0; i < 50; ++i) 
      cycle();
    digitalWrite(RST, HIGH);
    printState();
  }

  static void releaseBus() {
    if (digitalRead(RST) == HIGH) {
      digitalWrite(BUSRQ, LOW);
      while (digitalRead(BUSAK) != LOW) {
        cycle();
        printState();
      }
    }

    digitalWrite(RD, HIGH);
    digitalWrite(MREQ, HIGH);
    digitalWrite(ROM_WE, HIGH);
    digitalWrite(WR, HIGH);
  }

  static void takeOverBus() {
    if (digitalRead(RST) == HIGH) {
      digitalWrite(BUSRQ, HIGH);
      while (digitalRead(BUSAK) != HIGH) {
        cycle();
        printState();
      }
    }
  }

  static void printState() {
    if (digitalRead(MREQ) == LOW)
      Serial.print(AddressBus::getAddress());
    else
      Serial.print('?');
    Serial.print(' ');
    if (digitalRead(MREQ) == LOW)
      Serial.print(DataBus::getData());
    else
      Serial.print('?');
    Serial.print(" : ");
    Serial.print(digitalRead(M1));
    Serial.print(' ');
    Serial.print(digitalRead(MREQ));
    Serial.print(' ');
    Serial.print(digitalRead(WR));
    Serial.print(' ');
    Serial.print(digitalRead(RD));
    Serial.print(' ');
    Serial.print(digitalRead(BUSAK));
    Serial.print(' ');
    Serial.print(digitalRead(IORQ));
    Serial.println();
  }

};

class ROM {
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
    delayMicroseconds(100);
    uint8_t data = DataBus::getData();
    // for (;;);
    digitalWrite(RD, HIGH);
    digitalWrite(MREQ, HIGH);
    pinMode(RD, INPUT);
    pinMode(MREQ, INPUT);
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
    digitalWrite(wrPin, HIGH);
    digitalWrite(MREQ, HIGH);
    pinMode(wrPin, INPUT);
    pinMode(MREQ, INPUT);
    delayMicroseconds(100);

    for (size_t i = 0; i < 1000; ++i) {
      if (read(addr) == data)
        return true;
      delayMicroseconds(100);
    }

    return false;
  }

};

void setup() {
  Serial.begin(9600);
  Z80::initialize();
  ROM::initialize();
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    switch (c) {

      case 'h':  // acknowledgement
        Serial.println('+');
        break;

      case 'r': {  // read byte from memory position
        uint32_t addr = Serial.parseInt();
        Z80::releaseBus();
        Serial.println(ROM::read(addr));
        break;
      }

      case 'w': {   // write byte to memory position
        uint32_t addr = Serial.parseInt();
        uint8_t data = Serial.parseInt();
        Z80::releaseBus();
        bool success = ROM::write(addr, data);
        Serial.println(success ? '+' : 'x');
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

      case 'b':   // request Z80 bus
        Z80::releaseBus();
        Serial.println('+');
        break;

      case 'B':   // make Z80 take over bus
        Z80::takeOverBus();
        Serial.println('+');
        break;

      case '?':   // request Z80 state
        Z80::printState();
        break;
      
      case 10:  // ignore line breaks
      case 13:
        break;
      
      default:  // command not recognized
        Serial.println('x');
    }
  }
}
