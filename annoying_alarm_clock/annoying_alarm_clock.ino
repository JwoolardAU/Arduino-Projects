// Patrick Woolard

// March 3rd 2022

// This file contains the code necessary to run what I have come to call the "annoying alarm clock."
// Assuming all the pins are in the correct places on the arduino board, this program will randomly
// mildy annoying method of turning off a much less mildly annoying alarm sound. Each method of turning
// the alarm off is explained in more detail in the video and one-page description for the project. The
// alarm will sound for some number of minutes (which can be changed as desired by changing alarmTime variable) 
// and a countdown to the alarm will be provided in the serial monitor. Instructions on how to turn off the
// individual alarm methods will also be hinted at in the serial monitor. The primary goal of this annoying
// alarm clock is to annoy the user to a state of being more awake.


// IMPORTANT CODE INTEGRITY STATEMENT: 
// Any code relating to interacting with the alarm clock components (i.e. servo, joystick, etc.) was
// obtained through the Elegoo lesson PDFs present in the "Elegoo Documents" folder on my VM. I learned 
// everything used to make this project through those PDFs. The only other time I had to look something
// up was for the random() function and I provide a link to where I found that down below. Any other code
// was written by me alone.



// Necessary Libraries 
// In order to get the project run I did have to shuffle files around from the "Elegoo Documents" folder
// to resolve any dependancies needed for the alarm clock components
#include "IRremote.h"
#include "IR.h"
#include <Servo.h>


// Alarm & Timing variables
long alarmTime = 2; // how many minutes until alarm goes off
long elapTime = 1; // how many minutes have passed (starts at 1 on purpose for formatting later on)
int alarmMethod; // random method of turning alarm off

// Remote initializations
int rembut; // which button of the remote do you need to push (this also gets reused for other alarm methods)
IRrecv irrecv(RECEIVER);     // create instance of 'irrecv'
decode_results results;      // create instance of 'decode_results'

// Buzzer pin assignment
int buzzer = 12;//the pin of the active buzzer

// Tilt ball switch assignment
int tbs = 2;//the pin of the tilt ball switch

// Joystick pin addignments
const int SW_pin = 4; // digital pin connected to switch output
const int X_pin = 0; // analog pin A0 connected to X output
const int Y_pin = 1; // analog pin A1 connected to Y output

// servo object
Servo myservo;

// thermistor and fan pin assignments
int tempPin = 4; // pin A4
#define ENABLE 5
#define DIRA 3
#define DIRB 7

void setup()
{
  // various pin I/O set-up and serial monitor set-up
  pinMode(buzzer,OUTPUT);//initialize the buzzer pin as an output
  pinMode(tbs,INPUT); //initialize tilt ball switch as input
  digitalWrite(tbs, HIGH); 
  pinMode(SW_pin, INPUT);//initialize joystick switch
  digitalWrite(SW_pin, HIGH); 
  myservo.attach(9);//connect pin 9 with the control line(the middle line of Servo) 
  myservo.write(45);// move servos to center position -> 45° 
  // (45° is just a start value to ensure that if the servo moves, the user will see it move).
  
  Serial.begin(9600);// begin serial monitor

  // noise in empty port helps randomize seed need for all random num generation
  randomSeed(analogRead(0));

  // IR enabled
  irrecv.enableIRIn();

  //setting pin direction for fan motor
  pinMode(ENABLE,OUTPUT);
  pinMode(DIRA,OUTPUT);
  pinMode(DIRB,OUTPUT);
  
}



void loop()
{
  // pick randomly some method of turning off alarm
  delay(1000); // delay helps prevent board from skipping over alarm method selection
  alarmMethod = random(0,5); // random() comes from https://www.arduino.cc/reference/en/language/functions/random-numbers/random/
  delay(1000); // delay helps prevent board from skipping over alarm method selection
  //alarmMethod = ?; // Replace ? with method number for testing certain methods
  //Serial.print("Random Value: "); // Just for testing
  //Serial.println(alarmMethod);    // Just for testing
  
  
  Serial.print("Minutes left until alarm goes off: ");
  Serial.println(alarmTime);  
  Serial.println("");// whitespace


  // Countdown until alarm goes off
  while(elapTime <= alarmTime){ // alarm has not yet gone off
  delay(60000); // delay for 1 minute
  Serial.print("One minute has passed! Minutes left until alarm goes off: ");
  Serial.println(alarmTime - elapTime);
  elapTime++;
  }

  // SOUND THE ALARM!!!
  digitalWrite(buzzer,HIGH); 


  // Methods of turning off alarm:
  
  if (alarmMethod == 0) // person must use remote to turn off alarm as instructed by serial monitor
  {
    for (int i = 0; i < 3; i++) { // must use correct button 3 times

    
    rembut = random(0,10); // which number on remote we will need to press (0 inclusive - 10 exclusive)
    Serial.print("remote button: ");
    Serial.println(rembut);
    Serial.print("How many more correct button pushes: ");
    Serial.println(3-i);
    
    while(1){ // Continously be on the look out for user input
      
      irrecv.decode(&results); // what did the user press
      
      if(results.value == 0xFF6897 && rembut == 0){    // if the user needed to press 0 and they did so
         break;
      }
      else if(results.value == 0xFF30CF && rembut == 1){ // same as above but for 1
        break;
      }
      else if(results.value == 0xFF18E7 && rembut == 2){ // same as above but for 2
        break;
      }
      else if(results.value == 0xFF7A85 && rembut == 3){ // I think you get the idea from here...
        break;
      }
      else if(results.value == 0xFF10EF && rembut == 4){
        break;
      }
      else if(results.value == 0xFF38C7 && rembut == 5){
        break;
      }
      else if(results.value == 0xFF5AA5 && rembut == 6){
        break;
      }
      else if(results.value == 0xFF42BD && rembut == 7){
        break;
      }
      else if(results.value == 0xFF4AB5 && rembut == 8){
        break;
      }
      else if(results.value == 0xFF52AD && rembut == 9){
        break; 
      }
      else{ // when the user does nothing, do nothing.
        ;
      }
      irrecv.resume(); // obtain new input from user if necessary
      delay(500); // slight delay for performance boost (just from my observations)
    }

    }

  }
  else if (alarmMethod == 1){ // User must tilt breadboard for what seems like 5 seconds continously
    while(1){
      int digitalVal = digitalRead(tbs); //read tbs pin to see if they are tilting board
      if(HIGH == digitalVal){
        Serial.println("Hold Circuit upside down for 5 seconds");
        delay(5000);
        digitalVal = digitalRead(tbs); //read tbs pin again to see if they are still holding it
        if(HIGH == digitalVal){
          break;
        }
      }
    }
  }
  else if (alarmMethod == 2){ // User must move joystick according to serial monitor's directions.

    for (int i = 0; i < 4; i++) { // they must move it correctly 4 times
      
    
    rembut = random(0,4); // which of the four directions should they move it?

    if(rembut == 0){
      Serial.println("Move Joystick to the back left.");
      while(1){ // wait until the user move the joystick to the back left
        if(analogRead(X_pin) > 1000 && analogRead(Y_pin) > 1000){
          break;
        }
      }
    }
    else if(rembut == 1){
      Serial.println("Move Joystick to the back right.");
      while(1){ // wait until the user move the joystick to the back right
        if(analogRead(X_pin) > 1000 && analogRead(Y_pin) < 50){
          break;
        }
      }
    }
    else if(rembut == 2){
      Serial.println("Move Joystick to the front left.");
      while(1){ // wait until the user move the joystick to the front left
        if(analogRead(X_pin) < 50 && analogRead(Y_pin) > 1000){
          break;
        }
      }
    }
    else{
      Serial.println("Move Joystick to the front right.");
      while(1){ // wait until the user move the joystick to the front right
        if(analogRead(X_pin) < 50 && analogRead(Y_pin) < 50){
          break;
        }
      }
    }
    

    }
  }
  else if(alarmMethod == 3){ // User must follow the direction of the servo with the joystick and
                             // keep the button pressed at all times. 

    for (int i = 0; i < 20; i++){ // They could do this potentially up to 20 times, but it can happen
                                  // very quickly as they could already be in the right spot.
      
    
    rembut = random(0,2); // do we move the servo left or right?

    if(rembut == 0){
      myservo.write(0); // left
      Serial.println("Look at servo and push joystick down.");
      while(1){ // wait until user does as told
        if(digitalRead(SW_pin) == 0 && analogRead(Y_pin) > 1000){
          break;
        }
      }
    }
    else{
      myservo.write(180); // right
      Serial.println("Look at servo and push joystick down.");
      while(1){ // wait until user does as told
        if(digitalRead(SW_pin) == 0 && analogRead(Y_pin) < 50){
          break;
        }
      }
    }


    }// end for
  }// end else if
  else if(alarmMethod == 4){ // User must cool thermistor with fan

  // Code for temperature calculation obtained from thermometer Elegoo lesson PDF
  int tempReading = analogRead(tempPin); // obtaining temperature from thermistor
  double tempK = log(10000.0 * ((1024.0 / tempReading - 1)));
  tempK = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * tempK * tempK )) * tempK ); //  Temp Kelvin
  float tempC = tempK - 273.15;            // Convert Kelvin to Celcius
  float tempF = (tempC * 9.0)/ 5.0 + 32.0; // Convert Celcius to Fahrenheit. This is our starting temp
  
  
  Serial.print("Current Temperature: ");
  Serial.print(tempF);
  Serial.println("°F");
  Serial.println("Cool the thermistor with the fan by 5°F");
  delay(5000);

  
  //fan on full speed
  analogWrite(ENABLE,255); //enable on
  digitalWrite(DIRA,HIGH); //one way full speed
  digitalWrite(DIRB,LOW);

  while(1){ // keep reading temperature until it cools down by 5 °F
    int tempReading = analogRead(tempPin); // obtaining new temperature from thermistor
  double tempK = log(10000.0 * ((1024.0 / tempReading - 1)));
  tempK = 1 / (0.001129148 + (0.000234125 + (0.0000000876741 * tempK * tempK )) * tempK );       //  Temp Kelvin
  float tempC = tempK - 273.15;            // Convert Kelvin to Celcius
  float newTempF = (tempC * 9.0)/ 5.0 + 32.0; // Convert Celcius to Fahrenheit. This is our new temp
  Serial.print("New Temperature: ");
  Serial.print(newTempF);
  Serial.println("°F");
    if (newTempF < tempF - 5){ // determine wether or not new temp if 5°F cooler or not
      break;
    }
  }
    digitalWrite(ENABLE,LOW); // disable fan
  }
  else{ // This should never happen given the range of alarmMethod...
    Serial.print("No alarm method selected. Retrying..."); // ...but just in case we just inform the user and move on.
  }



 
  digitalWrite(buzzer,LOW);// Turn off the REALLY annoying buzzer
  elapTime = 1; // reset elapTime to original value
  Serial.print("You will now have to wait ");
  Serial.print(alarmTime);
  Serial.println(" minutes again. Disconnect clock to turn off completely.");
  delay(5000); // Give the user the chance to decide if they want to continue using current timer or not
} 
