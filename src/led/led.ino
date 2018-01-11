/* Voice commands to control a RGB LED: This is a LED monitor Agent to be managed
 * from the Deep Learning Agent (Speech Recognition) written in Python.
 *
 * Created by: Abián Torres Torres
 * Coded on: 17-11-2017
 * email: abiantorres.generic@gmail.com */

/* List of voice commands:
 * 1. Turn On
 * 2. Turn Off
 * 3. Switch Random Color
 * 4. Color Blink
 * 5. Normal Blink
 * 6. Decrease Swap Frecuency
 * 7. Increase Swap Frecuency */
 
// LED:
# define LED_RED_PIN 5 // LED connected to digital output pin 9 for red color.
# define LED_GREEN_PIN 7 // LED connected to digital output pin 9 for green color.
# define LED_BLUE_PIN 6 // LED connected to digital output pin 9 for blue color.
# define LED_MAX_VALUE 255 // Maximun value for LED.
# define LED_MIN_VALUE 0 // Minimum value for LED.
# define LED_SWAP_FRECUENCY_RATIO 100 // Value with which be used to modified the fading frecuency.
# define MAXIMUM_SWAP_FRECUENCY_RATIO 30000 // Value with which be used to modified the fading frecuency.
// Colors:
# define NUMBER_OF_COLORS 6 // Number of colors allowed in our system.
# define RGB_DIMENSION 3 // RGB Dimensions
// List of colors indexed in COLORS array:
# define WHITE 1
# define BLUE 2
# define RED 3
# define GREEN 4
# define GRAY 5
# define YELLOW 6
const int COLORS[NUMBER_OF_COLORS][RGB_DIMENSION] = {{255, 255, 255}, {0, 0, 255}, {255, 0, 0}, {0, 255, 0}, {128, 128, 128}, {255, 255, 0}};
// Transmission with computer:
# define TRANSMISSION_BAUD 9600

// LED:
int currentLedSwapFrecuency = LED_SWAP_FRECUENCY_RATIO * 5; // Value with will determinate the current fading frecuency of the LED.
// Colors:
int currentLedColor = WHITE; // Current LED color.
int randomColor[2] = {RED, WHITE}; // Temporal variable wich allows to get a random color in two sets excluding current LED color.
// Auxiliar variables for command selection:
int prevCommand = 0;
int nextCommand = 0;

// Set led values for each color:
void setLedValues(int redValue, int greenValue, int blueValue) {
  analogWrite(LED_RED_PIN, redValue);
  analogWrite(LED_GREEN_PIN, greenValue);
  analogWrite(LED_BLUE_PIN, blueValue);
}

// Command to change to a LED random color
void switchRandomColor(){
  randomColor[0] = random(currentLedColor);
  if(currentLedColor != NUMBER_OF_COLORS) {
    randomColor[1] = random(currentLedColor + 1, NUMBER_OF_COLORS + 1);
    currentLedColor = randomColor[random(2)];
  }
  else
    currentLedColor = randomColor[0];
  setLedValues(COLORS[currentLedColor][0], COLORS[currentLedColor][1], COLORS[currentLedColor][2]);
}

// Command to set LED intensity to minimun value
void turnOff() {
  setLedValues(LED_MIN_VALUE, LED_MIN_VALUE, LED_MIN_VALUE);
}

// Command to set LED intensity to maximun values
void turnOn() {
  setLedValues(COLORS[currentLedColor][0], COLORS[currentLedColor][1], COLORS[currentLedColor][2]);
}

void increaseSwapFrecuency() {
  if((currentLedSwapFrecuency + LED_SWAP_FRECUENCY_RATIO) <= MAXIMUM_SWAP_FRECUENCY_RATIO)
    currentLedSwapFrecuency = currentLedSwapFrecuency + LED_SWAP_FRECUENCY_RATIO;
}

void decreaseSwapFrecuency() {
  if((currentLedSwapFrecuency - LED_SWAP_FRECUENCY_RATIO) >= LED_SWAP_FRECUENCY_RATIO)
    currentLedSwapFrecuency = currentLedSwapFrecuency - LED_SWAP_FRECUENCY_RATIO;
}

// Command to make the LED Blink:
void normalBlink() {
  turnOn();
  delay(currentLedSwapFrecuency);
  turnOff();
  delay(currentLedSwapFrecuency);
}

void rules() {
  switch(nextCommand){
    case 1: // Turn On
      turnOn();
      break;
    case 2: // Turn Off
      turnOff();
      break;
    case 3: // Switch Random Color
      delay(currentLedSwapFrecuency);
      switchRandomColor();
      nextCommand = 0; // Avoid loops.
      prevCommand = 0;
      break;
    case 4: // Color Blink
      delay(currentLedSwapFrecuency);
      switchRandomColor(); // Allows loops.
      break;
    case 5: // Normal Blink
      turnOn();
      delay(currentLedSwapFrecuency);
      turnOff();
      delay(currentLedSwapFrecuency);
      // Allows loops.
      break;
    case 6: // Increase Swap Frecuency
      increaseSwapFrecuency();
      nextCommand = prevCommand;
      break;
    case 7: // Decrease Swap Frecuency
      decreaseSwapFrecuency();
      nextCommand = prevCommand;
      break;
    default:
      break;
  }
}

// Setup our Arduino configuration:
void setup() {
  randomSeed(analogRead(A5)); // Generate a seed for get random colors when the command 'Switch Random Color' is executed.
  // Pins
  pinMode(LED_RED_PIN, OUTPUT); // Declare the LED_RED_PIN as an OUTPUT.
  pinMode(LED_GREEN_PIN, OUTPUT); // Declare the LED_GREEN_PIN as an OUTPUT.
  pinMode(LED_BLUE_PIN, OUTPUT); // Declare the LED_BLUE_PIN as an OUTPUT.
  Serial.begin(TRANSMISSION_BAUD);  // Use the serial port.
  while (!Serial) {;} // wait for serial port to connect. Needed for native USB port only
}

void loop() {
  if (Serial.available() > 0){ // If Python3 module send a order:
    prevCommand = nextCommand; // Keep the last command to make sure that some commands behavoir is the required.
    nextCommand = Serial.parseInt(); // Get next command.
  }
  rules(); // Execute the current rule.
}
