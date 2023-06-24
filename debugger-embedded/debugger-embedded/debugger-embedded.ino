typedef enum {
  D0 = 16, D1 = 18, D2 = 12, D3 = 4, D4 = 2, D5 = 6, D6 = 8, D7 = 14,
  A0_ = 65, A1_ = 63, A2_ = 61, A3_ = 59, A4_ = 57, A5_ = 55, A6_ = 62, A7_ = 60,
  A8_ = 58, A9_ = 56, A10_ = 54, A11_ = 10, A12_ = 11, A13_ = 9, A14_ = 7, A15_ = 5,
  A16_ = 24, A17_ = 69, A18_ = 39,
  INT = 20, CLK = 3, NMI = 22, MREQ = 26, IORQ = 28, M1 = 33, RST = 35, BUSRQ = 37,
  BUSAK = 41, WR = 43, RD = 45, ROM_WE = 47,
} Pin;

class Z80 {
public:
  static void initialize() {
    pinMode(CLK, OUTPUT);
    pinMode(RST, OUTPUT);
  }

  static void cycle() {
    digitalWrite(CLK, HIGH);
    delayMicroseconds(100);
    digitalWrite(CLK, LOW);
    delayMicroseconds(100);
  }

  static void reset() {
    digitalWrite(RST, LOW);
    for (size_t i = 0; i < 50; ++i)
      cycle();
    digitalWrite(RST, HIGH);
  }
  
};

void setup() {
  Z80::initialize();
  Z80::reset();
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    char c = Serial.read();
    switch (c) {
      case 'h':
        Serial.println('+');
        break;
      case 10:
      case 13:
        break;  // ignore line breaks
      default:
        Serial.println('x');
    }
  }
}
