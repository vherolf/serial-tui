// serial tester 
//   prints out a counter
//   reads in Integers and resets counter
int DELAY = 100;

const int ledPin = LED_BUILTIN;
int ledState = LOW;
unsigned long previousMillis = 0;
const long interval = 1000;

unsigned long counter = 0;

void setup() {
  // initialize serial:
  Serial.begin(115200);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  // if there's any serial available, read it:
  while (Serial.available() > 0) {
    int times = Serial.parseInt();
    // look for the newline. That's the end of your sentence:
    if (Serial.read() == '\n') {
        counter = times;
        //digitalWrite(LED_BUILTIN, HIGH);
        //delay(DELAY*times);
        //digitalWrite(LED_BUILTIN, LOW);
        //delay(DELAY); 
        //Serial.println(times);
    }
  }
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;
    if (ledState == LOW) {
      ledState = HIGH;
    } else {
      ledState = LOW;
    }
    digitalWrite(ledPin, ledState);
    counter = counter + 1;
    Serial.println(counter);
  }
}
