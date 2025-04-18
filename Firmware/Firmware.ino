#include <WiFi.h>
#include <HTTPClient.h>

// لیست اینترنت های مجاز همراه پسورد
const char* ssidList[] = {
  "SHAHAB-2.4",
  "SHAHAB-5",
  "saeed144"
};

const char* passwordList[] = {
  "shahab220@",
  "shahab220@",
  "1373.144"
};

// لیست پایه ها
const int WIFI_LED = 2;

// متغیرهای عمومی
const int numNetworks = sizeof(ssidList) / sizeof(ssidList[0]);

// آدرس سایت
const char* webapp = "http://127.0.0.1:5000";

void setup() {
  // راه اندازی سریال مانیتورینگ
  delay(500);
  Serial.begin(115200);
  // تعریف پایه های ورودی و خروجی
  pinMode(WIFI_LED, OUTPUT);
  digitalWrite(WIFI_LED, LOW);  // خاموش کردن LED در ابتدا
  // اتصال به اینترنت
  bool connected = tryConnectToWiFi();
  if (connected) {
    digitalWrite(WIFI_LED, HIGH);  // LED ثابت روشن
    // sendGETRequest("/get_national_ids");
    // sendGETRequest("/get_reservation");
  } else {
    Serial.println("No network available!.");
    digitalWrite(WIFI_LED, LOW);  // LED خاموش
  }

}

void loop() {

}

// تابع اتصال به یکی از SSIDها
bool tryConnectToWiFi() {
  for (int i = 0; i < numNetworks; i++) {
    Serial.printf("Connecting to SSID: %s (%s)\n", ssidList[i], passwordList[i]);
    WiFi.begin(ssidList[i], passwordList[i]);

    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
      // چشمک زدن LED در زمان اتصال
      digitalWrite(WIFI_LED, HIGH);
      delay(250);
      digitalWrite(WIFI_LED, LOW);
      delay(250);
      Serial.print(".");
      attempts++;
    }

    if (WiFi.status() == WL_CONNECTED) {
      Serial.println("\n✅ Connected!");
      Serial.print("📶 SSID: ");
      Serial.println(ssidList[i]);
      Serial.print("💻 IP: ");
      Serial.println(WiFi.localIP());
      return true;
    } else {
      Serial.println("\n❌ Failed to connect...");
      WiFi.disconnect();
      delay(1000);
    }
  }

  return false;  // هیچ شبکه‌ای وصل نشد
}

