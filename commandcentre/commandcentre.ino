#include <WiFi.h>
#include <PubSubClient.h>

// --- 1. WiFi & Hotspot Settings ---
const char* ssid     = "AK";           // Your phone's hotspot name
const char* password = "nt2024cm";     // Your phone's hotspot password

// --- 2. MQTT Broker Settings ---
const char* mqtt_server = "10.204.132.164"; // Your laptop's IP address
const int   mqtt_port   = 1883;             // Standard MQTT port

WiFiClient espClient;
PubSubClient client(espClient);

// --- 3. Pin Definitions ---
const int WATER_PIN = 34; // Water sensor analog signal
const int GAS_PIN   = 35; // MQ Gas sensor digital output (D0)

// Motor Pins (Held LOW to prevent unexpected running)
const int IN1 = 26;
const int IN2 = 27;
const int IN3 = 14;
const int IN4 = 12;

unsigned long lastMsgTime = 0; 

void setup_wifi() {
  delay(10);
  Serial.print("Connecting to Wi-Fi: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.print("ESP32 IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    String clientId = "AegisMule-" + String(random(0xffff), HEX);
    if (client.connect(clientId.c_str())) {
      Serial.println("Connected to MQTT Broker!");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Trying again in 5 seconds...");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);

  // Initialize motor control pins as outputs and lock them LOW
  pinMode(IN1, OUTPUT); digitalWrite(IN1, LOW);
  pinMode(IN2, OUTPUT); digitalWrite(IN2, LOW);
  pinMode(IN3, OUTPUT); digitalWrite(IN3, LOW);
  pinMode(IN4, OUTPUT); digitalWrite(IN4, LOW);

  // Initialize sensor pins
  pinMode(WATER_PIN, INPUT);
  pinMode(GAS_PIN, INPUT);

  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Publish sensor data every 1 second
  unsigned long now = millis();
  if (now - lastMsgTime > 1000) {
    lastMsgTime = now;

    // Read Sensors
    int waterValue = analogRead(WATER_PIN);
    int gasDetected = digitalRead(GAS_PIN); // LOW or HIGH depending on threshold

    // Publish to MQTT
    client.publish("aegis/mule/water", String(waterValue).c_str());
    client.publish("aegis/mule/gas", gasDetected == LOW ? "ALERT: Gas Detected" : "NORMAL");

    // Print to Serial Monitor
    Serial.print("Water Level: ");
    Serial.print(waterValue);
    Serial.print(" | Gas Status: ");
    Serial.println(gasDetected == LOW ? "ALERT" : "NORMAL");
  }
}