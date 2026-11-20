/*
 * Stage 1 bench test: one LED per color connected directly to the NodeMCU.
 * Red: D1, Yellow: D2, Green: D5. Use one 220 ohm resistor per LED.
 */
#define RED_PIN D1
#define YELLOW_PIN D2
#define GREEN_PIN D5

void setup() {
  pinMode(RED_PIN, OUTPUT);
  pinMode(YELLOW_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  digitalWrite(RED_PIN, LOW);
  digitalWrite(YELLOW_PIN, LOW);
  digitalWrite(GREEN_PIN, LOW);
}

void loop() {
  digitalWrite(RED_PIN, HIGH);
  delay(3000);
  digitalWrite(RED_PIN, LOW);

  digitalWrite(YELLOW_PIN, HIGH);
  delay(1000);
  digitalWrite(YELLOW_PIN, LOW);

  digitalWrite(GREEN_PIN, HIGH);
  delay(3000);
  digitalWrite(GREEN_PIN, LOW);
}
