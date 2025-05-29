


/*
// 2, 3번 실행시킬 코드
// 🔥 통합 화재 감지 시스템 (MQ2 + Flame + DHT22 + LED + Buzzer)
#include <DHT.h>

// ✅ 핀 설정
#define MQ2_PIN A0
#define FLAME_PIN D2
#define DHT_PIN D7
#define DHT_TYPE DHT22
#define LED_PIN D5
#define BUZZER_PIN D6

DHT dht(DHT_PIN, DHT_TYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(2000);  // DHT 센서 안정화

  pinMode(FLAME_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(LED_PIN, LOW);
  noTone(BUZZER_PIN);
}

void loop() {
  // ✅ 센서 값 읽기
  int mq2_value = analogRead(MQ2_PIN);
  int flame_state = digitalRead(FLAME_PIN);  // LOW = 감지됨
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // ✅ 시리얼 출력 (모델 입력용으로 간결화)
  Serial.println("\n📡 [센서 데이터 측정값]");
  Serial.print("MQ2: "); Serial.println(mq2_value);
  Serial.print("Flame: "); Serial.println(flame_state == LOW ? 1 : 0);
  Serial.print("Temp: "); Serial.println(temperature);
  Serial.print("Humidity: "); Serial.println(humidity);

  // ✅ 화재 판단 기준
  bool fire_detected = false;
  if (mq2_value >= 200 && flame_state == LOW && temperature > 24 && humidity < 100) {
    fire_detected = true;
  }

  // ✅ 출력 장치 작동
  if (fire_detected) {
    digitalWrite(LED_PIN, HIGH);
    tone(BUZZER_PIN, 3000);  // 3kHz 큰 소리
    delay(500);
    digitalWrite(LED_PIN, LOW);
    noTone(BUZZER_PIN);
    delay(500);
  } else {
    digitalWrite(LED_PIN, LOW);
    noTone(BUZZER_PIN);
    delay(1000);
  }
}
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <Wire.h>
#include <LiquidCrystal_PCF8574.h>
#include <DHT.h>

const char* ssid = "13504_2GHz";
const char* password = "1350413504";
const char* serverUrl = "192.168.0.27:5000";

#define MQ2_PIN A0
#define FLAME_PIN D2
#define DHT_PIN D7
#define DHT_TYPE DHT22
#define LED_PIN D5
#define BUZZER_PIN D6

DHT dht(DHT_PIN, DHT_TYPE);
LiquidCrystal_PCF8574 lcd(0x27);

unsigned long previousMillis = 0;
const long interval = 5000;

void setup() {
  Wire.begin(D3, D4);
  Serial.begin(9600);
  dht.begin();
  delay(2000);

  pinMode(FLAME_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);

  lcd.begin(16, 2);
  lcd.setBacklight(255);
  lcd.setCursor(0, 0);
  lcd.print("Fire Monitor Ready");
  delay(2000);
  lcd.clear();

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    int mq2_value = analogRead(MQ2_PIN);
    int flame_state = digitalRead(FLAME_PIN);
    float temperature = dht.readTemperature();
    float humidity = dht.readHumidity();

    Serial.println("\n📡 [센서 데이터]");
    Serial.print("MQ2: "); Serial.println(mq2_value);
    Serial.print("Flame: "); Serial.println(flame_state == LOW ? 1 : 0);
    Serial.print("Temp: "); Serial.println(temperature);
    Serial.print("Humidity: "); Serial.println(humidity);

    char line1[17], line2[17];
    snprintf(line1, 17, "MQ2:%4d F:%d    ", mq2_value, (flame_state == LOW ? 1 : 0));
    snprintf(line2, 17, "T:%4.1f H:%3.0f%%   ", temperature, humidity);

    lcd.setCursor(0, 0);
    lcd.print(line1);
    lcd.setCursor(0, 1);
    lcd.print(line2);

    bool fire_detected = false;
    if (mq2_value >= 200 && flame_state == LOW && temperature > 24 && humidity < 100) {
      fire_detected = true;
    }

    if (fire_detected) {
      digitalWrite(LED_PIN, HIGH);
      tone(BUZZER_PIN, 3000);
    } else {
      digitalWrite(LED_PIN, LOW);
      noTone(BUZZER_PIN);
    }

    // HTTP POST로 Flask 서버에 센서 데이터 전송
    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      String url = "http://" + String(serverUrl) + "/api/sensor-data";

      String jsonData = "{";
      jsonData += "\"mq2\":" + String(mq2_value) + ",";
      jsonData += "\"flame\":" + String(flame_state == LOW ? 1 : 0) + ",";
      jsonData += "\"temperature\":" + String(temperature) + ",";
      jsonData += "\"humidity\":" + String(humidity);
      jsonData += "}";

      WiFiClient client;
      http.begin(client, url);

      http.addHeader("Content-Type", "application/json");

      int httpResponseCode = http.POST(jsonData);

      if (httpResponseCode > 0) {
        String response = http.getString();
        Serial.println("POST Response: " + response);
      } else {
        Serial.println("POST Error: " + String(httpResponseCode));
      }
      http.end();
    } else {
      Serial.println("WiFi Disconnected");
    }
  }
}
