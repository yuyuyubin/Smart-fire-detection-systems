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
  int flame_state = digitalRead(FLAME_PIN);
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // ✅ 시리얼 출력
  Serial.println("\n📡 [센서 데이터 측정값]");
  Serial.print("MQ2 (가스 농도): "); Serial.println(mq2_value);
  Serial.print("Flame (불꽃 감지): "); Serial.println(flame_state == LOW ? "🔥 불꽃 감지됨" : "✅ 정상");
  Serial.print("온도 (°C): "); Serial.println(temperature);
  Serial.print("습도 (%): "); Serial.println(humidity);

  // ✅ 화재 판단 기준 (온도/습도 포함)
  bool fire_detected = false;
  if (mq2_value > 100 && flame_state == LOW || temperature > 23 || humidity < 50) {
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
