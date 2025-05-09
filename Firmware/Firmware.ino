#include <WiFi.h>              // کتابخانه اتصال به وایفای
#include <HTTPClient.h>        // کتابخانه ارسال درخواست اینترنتی
#include <ArduinoJson.h>       // کتابخانه جداسازی اطلاعات دریافت شده از طریق اینترنت
#include <Keypad.h>            // کتابخانه کار با کیپد
#include <SPI.h>               // کتابخانه رابط RFID
#include <MFRC522.h>           // کتابخانه کار با RFID
#include <Wire.h>              // کتابخانه راه اندازی نمایشگر
#include <Adafruit_GFX.h>      // کتابخانه راه اندازی نمایشگر
#include <Adafruit_SSD1306.h>  // کتابخانه راه اندازی نمایشگر
#include "Adafruit_HTU21DF.h"  // کتابخانه راه اندازی سنسور دما
#include <BH1750.h>            // کتابخانه راه اندازی سنسور نور


// لیست اینترنت های مجاز همراه پسورد
const char* ssidList[] = {
  "Galaxy A12A312",
  "MobinNet-816E",
  "Saeed144"
};
const char* passwordList[] = {
  "jsjh0296",
  "farzan@123",
  "1373.144"
};

const int numNetworks = sizeof(ssidList) / sizeof(ssidList[0]);  // تعداد وایفای ها

// لیست پایه ها
const int WIFI_LED = 2;
const int LOCK_PIN = 15;
const int RFID_SS = 5;
const int RFID_RST = 4;
const int TEMP_SENSOR_PIN = 17;
const int FAN = 16;
const int LAMP1 = 13;
const int LAMP2 = 17;
const int TABLE_LED = 3;


const char* webapp = "https://farzanlib.pythonanywhere.com";  // آدرس سایت


const int MAX_IDS = 10;                                                      // حداکثر تعداد قابل‌پشتیبانی کد ملی
String nationalIds[MAX_IDS];                                                 // تعریف آرایه‌ای برای ذخیره کد ملی‌ها
int nationalIdCount = 0;                                                     // شمارنده برای تعداد واقعی
String nationalIdsJson = "";                                                 // برای ذخیره پاسخ get_national_ids
String defaultIds = "{\"national_ids\": [\"0440386624\", \"0960162836\"]}";  // مقادیر پیشفرض کدملی

// آماده سازی کیپد
const byte ROWS = 4;
const byte COLS = 3;
char keys[ROWS][COLS] = {
  { '1', '2', '3' },
  { '4', '5', '6' },
  { '7', '8', '9' },
  { '*', '0', '#' }
};
byte rowPins[ROWS] = { 12, 14, 27, 26 };
byte colPins[COLS] = { 25, 33, 32 };
Keypad keypad = Keypad(makeKeymap(keys), rowPins, colPins, ROWS, COLS);
String input_national_id = "";
char key;
const int LOCK_WAIT = 7000;

// آماده سازی RFID
MFRC522 rfid(RFID_SS, RFID_RST);

// آماده سازی نمایشگر
Adafruit_SSD1306 display(128, 32, &Wire, -1);

// آماده سازی سنسور دما
Adafruit_HTU21DF htu = Adafruit_HTU21DF();

// آماده سازی سنسور نور
BH1750 lightMeter;

unsigned long int cnt = 0;

void setup() {
  // راه اندازی سریال مانیتورینگ
  delay(2000);
  Serial.begin(115200);
  Serial.println("🚀 Smart Library Booting...");
  // ستاپ اولیه RFID
  SPI.begin();
  rfid.PCD_Init();
  delay(500);
  Serial.println("🟢 RFID is Ready");
  // تعریف پایه های ورودی و خروجی
  pinMode(WIFI_LED, OUTPUT);
  digitalWrite(WIFI_LED, LOW);  // خاموش کردن LED در ابتدا
  pinMode(LOCK_PIN, OUTPUT);
  digitalWrite(LOCK_PIN, HIGH);  // قفل بسته
  pinMode(FAN, OUTPUT);
  digitalWrite(FAN, HIGH);  // فن خاموش
  pinMode(LAMP1, OUTPUT);
  pinMode(LAMP2, OUTPUT);
  digitalWrite(LAMP1, HIGH);  // لامپ ها روشن
  digitalWrite(LAMP2, HIGH);  // لامپ ها روشن
  pinMode(TABLE_LED, OUTPUT);
  digitalWrite(TABLE_LED, LOW); // لامپ میز خاموش
  delay(200);
  Serial.println("🟢 PINS are Ready");
  if (!htu.begin()) {
    Serial.println("Check circuit. HTU21D not found!");
    // while (1);
  }
  lightMeter.begin();
  Serial.println("🟢 Sensors are Ready");
  // راه اندازی نمایشگر
  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    Serial.println(F("SSD1306 allocation failed"));
    // while (true);
  }
  display.clearDisplay();
  display.setTextSize(1);
  display.setTextColor(SSD1306_WHITE);
  display.setCursor(0, 10);
  display.println(F("Start"));
  display.display();
  // اتصال به به اینترنت و دریافت کدملی ها
  bool connected = tryConnectToWiFi();
  if (connected) {
    digitalWrite(WIFI_LED, HIGH);  // LED ثابت روشن
    sendGETRequest("/get_national_ids");
  } else {
    Serial.println("No network available!.");
    digitalWrite(WIFI_LED, LOW);  // LED خاموش
  }
  Serial.println("🟢 System is Ready");
  display.clearDisplay();
}

void loop() {
  // 🟢 اسکن کارت RFID
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.println("🔍 Detected UID: " + uid);

    postUIDToServer("0960162836", uid);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    delay(1000);
  }

  // 🟢 گرفتن ورودی از کیپد به صورت
  char key = keypad.getKey();
  if (key) {
    Serial.print(key);
    if (key == '*') {
      Serial.println();
      // نمایش روی نمایشگر
      display.clearDisplay();
      display.setCursor(0, 0);
      display.println("ID:");
      display.setCursor(0, 20);
      display.println(input_national_id);
      display.display();
      if (isAuthorized(input_national_id)) {
        Serial.printf("✅ Access Granted for %s\n", input_national_id);
	    display.clearDisplay();
	    display.setCursor(0, 0);
	    display.println("Welcome!");
		display.display();
        unlockDoor();
      } else {
	    display.clearDisplay();
	    display.setCursor(0, 0);
	    display.println("XXX Not Registerd XXX");
		display.display();
        Serial.printf("❌ Access Denied for %s\n", input_national_id);
      }
      input_national_id = "";  // پاکسازی
      display.clearDisplay();
    } else {
      input_national_id += key;
      display.setCursor(0, 0);
      display.println("ID:");
      display.setCursor(0, 20);
      display.println(input_national_id);
      display.display();
    }
  }

  if ((cnt % 500 == 0)) {
    Serial.println("GET LIGHT & TEMPERATURE!");
    manageFan();
    manageLight();
  }
  
  
  if ((cnt % 1000 == 0)) {
    Serial.println("Check table reservation!");
    check_table();
  }
  

  cnt++;
  delay(1);
}

// مدیریت فن با توجه به دما
void manageFan() {
  float temp = htu.readTemperature();
  Serial.print("Temperature(°C): ");
  Serial.println(temp);

  if (temp > 28.0) {
    digitalWrite(FAN, LOW);
  } else {
    digitalWrite(FAN, HIGH);
  }
}

// مدیریت نور
void manageLight() {
  float lux = lightMeter.readLightLevel();
  Serial.print("Light(lux): ");
  Serial.println(lux);
  if (lux > 200) {
    digitalWrite(LAMP1, LOW);
    digitalWrite(LAMP2, LOW);
  } else {
    digitalWrite(LAMP1, HIGH);
    digitalWrite(LAMP2, HIGH);
  }
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

  nationalIdsJson = defaultIds;
  parseNationalIds(nationalIdsJson);
  return false;  // هیچ شبکه‌ای وصل نشد
}

// تابع ارسال درخواست GET به آدرس مشخص از سرور اپ
void sendGETRequest(const String& endpoint) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(webapp) + endpoint;

    const int maxRetries = 3;
    int attempt = 0;
    int responseCode = -1;
    String payload = "";

    while (attempt < maxRetries) {
      Serial.printf("🔗 Attempt %d: Requesting %s\n", attempt + 1, url.c_str());

      http.begin(url);
      responseCode = http.GET();

      if (responseCode == 200) {
        Serial.printf("📥 Status Code: %d\n", responseCode);
        payload = http.getString();
        Serial.println("📄 Response:");
        Serial.println(payload);

        if (endpoint == "/get_national_ids") {
          if (payload.indexOf("national_ids") != -1) {
            nationalIdsJson = payload;
            parseNationalIds(nationalIdsJson);  // ✅ فراخوانی جداسازی کد ملی ها
          } else {
            Serial.println("⚠️ National IDs not found, using default values.");
            nationalIdsJson = defaultIds;
            parseNationalIds(nationalIdsJson);  // ✅ فراخوانی پارس با مقدار پیش‌فرض
          }
        }
        break;  // موفق شد، از حلقه بیا بیرون
      } else {
        Serial.printf("⚠️ Request failed with status: %d\n", responseCode);
        http.end();
        delay(1000);  // یک ثانیه صبر کن و دوباره تلاش کن
      }

      attempt++;
    }

    if (responseCode != 200) {
      Serial.println("❌ Failed to get valid response after retries.");
      nationalIdsJson = defaultIds;
      parseNationalIds(nationalIdsJson);  // ✅ فراخوانی پارس با مقدار پیش‌فرض
    }

    http.end();  // اطمینان از آزادسازی منابع
  } else {
    Serial.println("🚫 Internet Problem!.");
  }
}

// تابع ارسال آیدی کتاب به اپ
void postUIDToServer(const String& uid, const String& buid) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(webapp) + "/add_rent";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    // ساخت داده شامل uid و buid
    String payload = "{\"nid\": \"" + uid + "\", \"buid\": \"" + buid + "\"}";

    int responseCode = http.POST(payload);
    Serial.printf("📤 POST /add_rent Status: %d\n", responseCode);

    if (responseCode > 0)
      Serial.println("📄 Response: " + http.getString());

    http.end();
  } else {
    Serial.println("🚫 Cannot send UID, no Internet");
  }
}

// ذخیره کد ملی ها
void parseNationalIds(const String& json) {
  // ایجاد فضای حافظه برای کد ملی ها
  const size_t capacity = JSON_ARRAY_SIZE(MAX_IDS) + 100;
  DynamicJsonDocument doc(capacity);

  DeserializationError error = deserializeJson(doc, json);
  if (error) {
    Serial.print("⚠️ JSON Parse failed: ");
    Serial.println(error.f_str());
    return;
  }

  JsonArray ids = doc["national_ids"];
  nationalIdCount = 0;

  for (String id : ids) {
    if (nationalIdCount < MAX_IDS) {
      nationalIds[nationalIdCount++] = id;
    }
  }

  // تست چاپ کد ملی‌ها
  Serial.println("📦 Extracted National IDs:");
  for (int i = 0; i < nationalIdCount; i++) {
    Serial.printf("  %d. %s\n", i + 1, nationalIds[i].c_str());
  }
}

// تابع بررسی وجود کد ملی در لیست
bool isAuthorized(String input) {
  for (int i = 0; i < nationalIdCount; i++) {
    if (nationalIds[i] == input) return true;
  }
  return false;
}

// تابع باز کردن درب
void unlockDoor() {
  digitalWrite(LOCK_PIN, LOW);
  Serial.println("🔓 Lock OPENED");
  delay(LOCK_WAIT);
  digitalWrite(LOCK_PIN, HIGH);
  Serial.println("🔒 Lock CLOSED");
}

// چک کردن رزرو بودن میز
void check_table() {
  String endpoint = "/get_reservation";
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(webapp) + endpoint;

    const int maxRetries = 2;
    int attempt = 0;
    int responseCode = -1;
    String payload = "";

    while (attempt < maxRetries) {
      Serial.printf("🔗 Attempt %d: Requesting %s\n", attempt + 1, url.c_str());

      http.begin(url);
      responseCode = http.GET();

      if (responseCode == 200) {
        payload = http.getString();
        Serial.println("📄 Response:");
        Serial.println(payload);

        // پارس کردن JSON
        const size_t capacity = JSON_OBJECT_SIZE(1) + JSON_OBJECT_SIZE(4) + 60;
        DynamicJsonDocument doc(capacity);

        DeserializationError error = deserializeJson(doc, payload);
        if (error) {
          Serial.print("⚠️ JSON Parse Error: ");
          Serial.println(error.c_str());
        } else {
          bool table1Status = doc["availability"]["table1"];
          if (table1Status) {
            digitalWrite(TABLE_LED, HIGH);
            Serial.println("✅ Table1 is available → LED ON");
          } else {
            digitalWrite(TABLE_LED, LOW);
            Serial.println("❌ Table1 is NOT available → LED OFF");
          }
        }

        break;  // موفق شد
      } else {
        Serial.printf("⚠️ Request failed with status: %d\n", responseCode);
		digitalWrite(TABLE_LED, LOW);
        http.end();
        delay(1000);
      }

      attempt++;
    }

    http.end();
  } else {
	digitalWrite(TABLE_LED, LOW);
    Serial.println("🚫 Internet Problem!.");
  }
}
