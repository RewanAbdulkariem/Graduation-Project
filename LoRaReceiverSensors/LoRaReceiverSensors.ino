#include <SPI.h>
#include <LoRa.h>

void setup() {
  Serial.begin(9600);
  while (!Serial);

  //Serial.println("LoRa Receiver");

  if (!LoRa.begin(434E6)) {
    //Serial.println("Starting LoRa failed!");
    while (1);
  }
}

void loop() {
  // Try to parse packet
  int packetSize = LoRa.parsePacket();
  
  if (packetSize) {
    // Received a packet
    //Serial.print("Received packet: ");

    // Read packet into a String
    String receivedMessage = "";
    while (LoRa.available()) {
      receivedMessage += (char)LoRa.read();
    }

    // Print received message
    Serial.println(receivedMessage);
/*
    // Parse received message to extract values
    float temperature = parseValue(receivedMessage, "Temperature:");
    float humidity = parseValue(receivedMessage, "Humidity:");
    float LPG = parseValue(receivedMessage, "LPG=");
    float CH4 = parseValue(receivedMessage, "CH4=");
    float CO = parseValue(receivedMessage, "CO=");
    float Alcohol = parseValue(receivedMessage, "Alcohol=");
    float Smoke = parseValue(receivedMessage, "Smoke=");

    // Print parsed values
    Serial.print("Temperature: ");
    Serial.print(temperature);
    Serial.println(" °C");
    Serial.print("Humidity: ");
    Serial.print(humidity);
    Serial.println(" %");
    Serial.print("Gas Readings - LPG: ");
    Serial.print(LPG);
    Serial.print(" ppm, CH4: ");
    Serial.print(CH4);
    Serial.print(" ppm, CO: ");
    Serial.print(CO);
    Serial.print(" ppm, Alcohol: ");
    Serial.print(Alcohol);
    Serial.print(" ppm, Smoke: ");
    Serial.print(Smoke);
    Serial.println(" ppm");

    // Print RSSI of packet
    Serial.print("RSSI: ");
    Serial.println(LoRa.packetRssi());
    */
  }
}

// Function to parse float value from a String
float parseValue(String data, String key) {
  int keyIndex = data.indexOf(key);
  if (keyIndex == -1) return NAN; // Key not found
  int startIndex = keyIndex + key.length(); // Start of the value
  int endIndex = data.indexOf(",", startIndex); // End of the value
  if (endIndex == -1) endIndex = data.length(); // If it's the last value
  String valueString = data.substring(startIndex, endIndex);
  return valueString.toFloat();
}
