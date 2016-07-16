#include <LiquidCrystal.h>

/* LCD settings */
#define CONTRAST  23
#define BACKLIGHT 28836

/* LCD pins */
#define PIN_CONTRAST  6
#define PIN_BACKLIGHT 9

#define PIN_RW 8
#define PIN_EN 7
#define PIN_D4 5
#define PIN_D5 4
#define PIN_D6 3
#define PIN_D7 2

LiquidCrystal lcd(PIN_RW, PIN_EN, PIN_D4, PIN_D5, PIN_D6, PIN_D7);

String inputString = "";        // String for buffering the message
boolean stringComplete = false; // Indicates if the string is complete
int curFanChar = 0;             // Current character of fan animation

byte fanChar1[8] = {
  0b00000,
  0b00000,
  0b01110,
  0b10101,
  0b11111,
  0b10101,
  0b01110,
  0b00000
};

byte fanChar2[8] = {
  0b00000,
  0b00000,
  0b01110,
  0b11011,
  0b10101,
  0b11011,
  0b01110,
  0b00000
};

byte celsius[8] = {
  0b01000,
  0b10100,
  0b01000,
  0b00011,
  0b00100,
  0b00100,
  0b00011,
  0b00000
};

void printInitialLCDStuff() {
  lcd.setCursor(0, 1);
  lcd.print("GPU:");
  lcd.setCursor(0, 2);
  lcd.print("Fan:");
  lcd.setCursor(0, 3);
  lcd.print("Core/Mem:");
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '|') {
      stringComplete = true;
    }
  }
}

void setup() {
  // Setup contrast and backlight
  analogWrite(PIN_CONTRAST, CONTRAST);
  analogWrite(PIN_BACKLIGHT, BACKLIGHT);
  
  // Setup LCD
  lcd.begin(20, 4);
  printInitialLCDStuff();
  
  // Setup serial
  Serial.begin(9600);
  inputString.reserve(200);

  // Create the custom characters
  lcd.createChar(0, fanChar1);
  lcd.createChar(1, fanChar2);
  lcd.createChar(2, celsius);
}

void loop() {
  serialEvent();
  if (stringComplete) {
    // CPU
    int cpuStringStart = inputString.indexOf("C");
    int cpuStringLimit = inputString.indexOf("|");
    String cpuString = inputString.substring(cpuStringStart + 1, cpuStringLimit);
    lcd.setCursor(0, 0);
    lcd.print(cpuString);
    
    // GPU 1
    int gpu1StringStart = inputString.indexOf("G", cpuStringLimit);
    int gpu1StringLimit = inputString.indexOf("|", gpu1StringStart);
    String gpu1String = inputString.substring(gpu1StringStart + 1 ,gpu1StringLimit);
    lcd.setCursor(5, 1);
    lcd.print(gpu1String);

    // GPU 2
    int gpu2StringStart = inputString.indexOf("F", gpu1StringLimit);
    int gpu2StringLimit = inputString.indexOf("|", gpu2StringStart);
    String gpu2String = inputString.substring(gpu2StringStart + 1 ,gpu2StringLimit);
    lcd.setCursor(5, 2);
    lcd.print(gpu2String);

    // GPU 3
    int gpu3StringStart = inputString.indexOf("g", gpu2StringLimit);
    int gpu3StringLimit = inputString.indexOf("|", gpu3StringStart);
    String gpu3String = inputString.substring(gpu3StringStart + 1 ,gpu3StringLimit);
    lcd.setCursor(10, 3);
    lcd.print(gpu3String);

    // Print fan animation
    lcd.setCursor(10, 2);
    lcd.write((uint8_t)curFanChar);
    curFanChar = !curFanChar;

    // Print celsius symbol in the appropriate positions
    lcd.setCursor(12, 1);
    lcd.write((uint8_t)2);

    // CPU core temps celsius symbols
    lcd.setCursor(7, 0);
    lcd.write((uint8_t)2);
    lcd.setCursor(11, 0);
    lcd.write((uint8_t)2);
    lcd.setCursor(15, 0);
    lcd.write((uint8_t)2);
    lcd.setCursor(19, 0);
    lcd.write((uint8_t)2);
    
    inputString = "";
    stringComplete = false;
  }
}
