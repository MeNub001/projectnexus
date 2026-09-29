#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// --- Network & MQTT Config ---
const char* ssid = "AK";
const char* password = "nt2024cm";
const char* mqtt_server = "10.204.132.164"; 

WiFiClient espClient;
PubSubClient client(espClient);

// --- Hardware Pin Definitions ---
// Motor Driver (L298N / TB6612FNG)
const int IN1 = 15; // Left Motor Fwd
const int IN2 = 2;  // Left Motor Rev
const int IN3 = 0;  // Right Motor Fwd
const int IN4 = 4;  // Right Motor Rev

// Encoders
const int LEFT_ENC_A = 33;
const int LEFT_ENC_B = 25;
const int RIGHT_ENC_A = 17;
const int RIGHT_ENC_B = 27;

// --- Encoder Tick Counters ---
volatile long leftTicks = 0;
volatile long rightTicks = 0;

// Interrupt Service Routines (ISRs) for Encoders
void IRAM_ATTR leftEncoderISR() {
  leftTicks++;
}

void IRAM_ATTR rightEncoderISR() {
  rightTicks++;
}

// --- Basic Movement Functions ---
void stopMotors() {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);
  digitalWrite(IN4, LOW);
  delay(500); // Pause between movements
}

void moveForward(long targetTicks) {
  leftTicks = 0; rightTicks = 0;
  
  digitalWrite(IN1, HIGH); digitalWrite(IN2, LOW);
  digitalWrite(IN3, HIGH); digitalWrite(IN4, LOW);
  
  // Wait until encoders reach the target distance
  while(leftTicks < targetTicks && rightTicks < targetTicks) {
    delay(10);
  }
  stopMotors();
}

void turnLeft(long targetTicks) {
  leftTicks = 0; 
  rightTicks = 0;
  
  // Flipped logic: Left goes forward, Right goes backward
  digitalWrite(IN1, HIGH); 
  digitalWrite(IN2, LOW);
  digitalWrite(IN3, LOW);  
  digitalWrite(IN4, HIGH); 
  
  while(leftTicks < targetTicks) {
    delay(10);
  }
  stopMotors();
}

void turnRight(long targetTicks) {
  leftTicks = 0; 
  rightTicks = 0;
  
  // Flipped logic: Left goes backward, Right goes forward
  digitalWrite(IN1, LOW);  
  digitalWrite(IN2, HIGH); 
  digitalWrite(IN3, HIGH); 
  digitalWrite(IN4, LOW);  
  
  while(rightTicks < targetTicks) {
    delay(10);
  }
  stopMotors();
}

// --- MQTT Callback & Path Execution ---
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.println("\n[SYS] Incoming Mission Trajectory...");

  StaticJsonDocument<512> doc;
  DeserializationError error = deserializeJson(doc, payload, length);

  if (error) {
    Serial.print("JSON Parse failed: ");
    Serial.println(error.c_str());
    return;
  }

  JsonArray route = doc["mission_route"].as<JsonArray>();

  Serial.println("Executing Route Sequence:");
  
  // Iterate through the array and execute hardcoded movements for each location
  for (JsonVariant waypoint : route) {
    String nodeName = waypoint.as<String>();
    Serial.print("Navigating to: ");
    Serial.println(nodeName);

    // Hardcoded demonstrator logic
    if (nodeName == "Balai Bomba Command Hub") {
      // Base node: Just flash an LED or do a short calibration wiggle
      moveForward(100);
      turnRight(50);
      turnLeft(50);
    } 
    else if (nodeName == "Simpang UTP Junction") {
      // Represents a long straight stretch
      moveForward(1500); 
    } 
    else if (nodeName == "Klinik Kesihatan Seri Iskandar") {
      // Represents a right turn and medium straight
      turnRight(350); 
      moveForward(800);
    } 
    else if (nodeName == "Jambatan Bota Kanan") {
      // Represents navigating a bridge
      moveForward(2000); 
    } 
    else if (nodeName == "SK Seri Iskandar") {
      // Represents a left turn into a facility
      turnLeft(350);
      moveForward(600);
    }
    else if (nodeName == "Dewan Serbaguna Bota") {
      turnRight(400);
      moveForward(1200);
    }
    else if (nodeName == "Lebuhraya High Ground Bypass") {
      // Long evasive maneuver
      turnLeft(200);
      moveForward(2500);
      turnRight(200);
    }
  }
  Serial.println("[SYS] Destination Reached. Awaiting next mission.");
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("RoverClient")) {
      Serial.println("connected");
      client.subscribe("aegis/rover/route");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Motor Pins Setup
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  
  // Encoder Pins Setup
  pinMode(LEFT_ENC_A, INPUT_PULLUP);
  pinMode(RIGHT_ENC_A, INPUT_PULLUP);
  // Optional: Read Channel B for directionality, but for basic forward/turn ticks, Channel A is sufficient
  pinMode(LEFT_ENC_B, INPUT_PULLUP); 
  pinMode(RIGHT_ENC_B, INPUT_PULLUP);

  // Attach Hardware Interrupts to counting functions
  attachInterrupt(digitalPinToInterrupt(LEFT_ENC_A), leftEncoderISR, RISING);
  attachInterrupt(digitalPinToInterrupt(RIGHT_ENC_A), rightEncoderISR, RISING);

  // Network Setup
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop(); 
}
