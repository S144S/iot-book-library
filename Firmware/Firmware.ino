#include <WiFi.h>         // کتابخانه اتصال به وایفای
#include <HTTPClient.h>   // کتابخانه ارسال درخواست اینترنتی
#include <ArduinoJson.h>  // کتابخانه جداسازی اطلاعات دریافت شده از طریق اینترنت
#include <Keypad.h>       // کتابخانه کار با کیپد
#include <SPI.h>          // کتابخانه رابط RFID
#include <MFRC522.h>      // کتابخانه کار با RFID


// لیست اینترنت های مجاز همراه پسورد
const char* ssidList[] = {
  "SHAHAB-2.4",
  "SHAHAB-5",
  "Saeed144"
};
const char* passwordList[] = {
  "shahab220@",
  "shahab220@",
  "1373.144"
};

const int numNetworks = sizeof(ssidList) / sizeof(ssidList[0]);  // تعداد وایفای ها

// لیست پایه ها
const int WIFI_LED = 2;
const int LOCK_PIN = 4;
const int RFID_SS = 5;
const int RFID_RST = 22;


const char* webapp = "http://192.168.100.108:5000";  // آدرس سایت


const int MAX_IDS = 10;                                                      // حداکثر تعداد قابل‌پشتیبانی کد ملی
String nationalIds[MAX_IDS];                                                 // تعریف آرایه‌ای برای ذخیره کد ملی‌ها
int nationalIdCount = 0;                                                     // شمارنده برای تعداد واقعی
String nationalIdsJson = "";                                                 // برای ذخیره پاسخ get_national_ids
String defaultIds = "{\"national_ids\": [\"0440386624\", \"0922213372\"]}";  // مقادیر پیشفرض کدملی

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

// راه اندازی RFID
MFRC522 rfid(RFID_SS, RFID_RST);


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
  delay(200);
  Serial.println("🟢 PINS are Ready");
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
}

void loop() {
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {
    String uid = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      uid += String(rfid.uid.uidByte[i], HEX);
    }
    uid.toUpperCase();
    Serial.println("🔍 Detected UID: " + uid);

    // postUIDToServer(uid);

    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    delay(1000);  // برای جلوگیری از ارسال چندباره
  }

  while (key != '*') {  // فشردن کلید * برای تایید
    key = keypad.getKey();
    if (key) {
      Serial.print(key);
      input_national_id += key;
    }
  }
  Serial.println();
  // پاک کردن * آخر
  input_national_id.remove(input_national_id.length() - 1);
  if (isAuthorized(input_national_id)) {
    Serial.printf("✅ Access Granted for %s\n", input_national_id);
    unlockDoor();
  } else {
    Serial.printf("❌ Access Denied for %s\n", input_national_id);
  }
  key = '#';
  input_national_id = "";
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
void postUIDToServer(const String& uid) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = String(webapp) + "/rent_book";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\"uid\": \"" + uid + "\"}";
    int responseCode = http.POST(payload);

    Serial.printf("📤 POST /rent_book Status: %d\n", responseCode);
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
