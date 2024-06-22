#include <SPI.h>
#include <LoRa.h>
#include <DHT.h>
#include <MQUnifiedsensor.h>

#define DHTPIN 3     // Digital pin connected to the DHT sensor
#define DHTTYPE DHT22   // DHT 22 (AM2302) sensor type

#define Board                 ("Arduino UNO")
#define MQ_PIN                A0  // Analog input 0 of your Arduino
#define Voltage_Resolution    5
#define ADC_Bit_Resolution    10

DHT dht(DHTPIN, DHTTYPE);
MQUnifiedsensor MQ4(Board, Voltage_Resolution, ADC_Bit_Resolution, MQ_PIN, "MQ-4");

// Thresholds for sensor readings
const float TEMP_THRESHOLD = 38.0;    // Temperature threshold in °C
const float CO_THRESHOLD = 101.0;     // CO concentration threshold in ppm
const float LPG_THRESHOLD = 200.0;    // LPG concentration threshold in ppm
const float CH4_THRESHOLD = 1000.0;   // CH4 concentration threshold in ppm
const float ALCOHOL_THRESHOLD = 500.0; // Alcohol concentration threshold in ppm
const float SMOKE_THRESHOLD = 500.0;  // Smoke concentration threshold in ppm

void setup() {
  Serial.begin(9600);
  while (!Serial);

  Serial.println("LoRa Sender with DHT22 and MQ4 Sensors");

  if (!LoRa.begin(434E6)) {
    Serial.println("Starting LoRa failed!");
    while (1);
  }

  dht.begin();  // Initialize DHT sensor
  MQ4.setRegressionMethod(1); // Set regression method
  MQ4.init();  // Initialize the MQ4 sensor

  // Calibration routine to set R0 value for MQ4 sensor
  Serial.print("Calibrating MQ4, please wait...");
  float calcR0 = 0;
  for (int i = 1; i <= 10; i++) {
    MQ4.update();
    calcR0 += MQ4.calibrate(4.4); // RatioMQ4CleanAir = 4.4 (for clean air)
    delay(500);  // Adjust delay as necessary
  }
  MQ4.setR0(calcR0 / 10);
  Serial.println(" Calibration done.");
}

void loop() {
  // Read from DHT sensor
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Read from MQ4 sensor
  MQ4.update();  // Update sensor data

  // Check thresholds and generate warning if conditions are not normal
  bool normalConditions = true;
  String warningMessage = "";

  // Check temperature threshold
  if (temperature > TEMP_THRESHOLD) {
    warningMessage += "High temperature detected! ";
    normalConditions = false;
  }

  // Check CO concentration threshold
  float CO = MQ4.readSensor();
  if (CO > CO_THRESHOLD) {
    warningMessage += "High CO concentration detected! ";
    normalConditions = false;
  }

  // Check LPG concentration threshold
  MQ4.setA(3811.9); MQ4.setB(-3.113); // LPG
  float LPG = MQ4.readSensor();
  if (LPG > LPG_THRESHOLD) {
    warningMessage += "High LPG concentration detected! ";
    normalConditions = false;
  }

  // Check CH4 concentration threshold
  MQ4.setA(1012.7); MQ4.setB(-2.786); // CH4
  float CH4 = MQ4.readSensor();
  if (CH4 > CH4_THRESHOLD) {
    warningMessage += "High CH4 concentration detected! ";
    normalConditions = false;
  }

  // Check Alcohol concentration threshold
  MQ4.setA(60000000000); MQ4.setB(-14.01); // Alcohol
  float Alcohol = MQ4.readSensor();
  if (Alcohol > ALCOHOL_THRESHOLD) {
    warningMessage += "High Alcohol concentration detected! ";
    normalConditions = false;
  }

  // Check Smoke concentration threshold
  MQ4.setA(30000000); MQ4.setB(-8.308); // Smoke
  float Smoke = MQ4.readSensor();
  if (Smoke > SMOKE_THRESHOLD) {
    warningMessage += "High Smoke concentration detected! ";
    normalConditions = false;
  }

  // Prepare message to send over LoRa
  String message = "Temperature: " + String(temperature) + "°C, Humidity: " + String(humidity) + "% | Gas Readings: ";
  message += "LPG=" + String(LPG) + " ppm, CH4=" + String(CH4) + " ppm, CO=" + String(CO) + " ppm, Alcohol=" + String(Alcohol) + " ppm, Smoke=" + String(Smoke) + " ppm";

  // Append warning message if conditions are not normal
  if (!normalConditions) {
    message += " | WARNING: " + warningMessage;
  }

  // Print message to Serial Monitor
  Serial.println(message);

  // Send message over LoRa
  LoRa.beginPacket();
  LoRa.print(message);
  LoRa.endPacket();

  delay(5000);  // Adjust delay as necessary
}
