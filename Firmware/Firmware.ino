#include <WiFi.h>         // کتابخانه اتصال به وایفای
#include <HTTPClient.h>   // کتابخانه ارسال درخواست اینترنتی
#include <ArduinoJson.h>  // کتابخانه جداسازی اطلاعات دریافت شده از طریق اینترنت

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


const char* webapp = "http://192.168.100.108:5000";  // آدرس سایت


const int MAX_IDS = 10;                                                      // حداکثر تعداد قابل‌پشتیبانی کد ملی
String nationalIds[MAX_IDS];                                                 // تعریف آرایه‌ای برای ذخیره کد ملی‌ها
int nationalIdCount = 0;                                                     // شمارنده برای تعداد واقعی
String nationalIdsJson = "";                                                 // برای ذخیره پاسخ get_national_ids
String defaultIds = "{\"national_ids\": [\"0440386624\", \"0922213372\"]}";  // مقادیر پیشفرض کدملی


void setup() {
  // راه اندازی سریال مانیتورینگ
  delay(2000);
  Serial.begin(115200);
  Serial.println("Welcome to the IoT Library 😊");
  // تعریف پایه های ورودی و خروجی
  pinMode(WIFI_LED, OUTPUT);
  digitalWrite(WIFI_LED, LOW);  // خاموش کردن LED در ابتدا
  // اتصال به به اینترنت و دریافت کدملی ها
  bool connected = tryConnectToWiFi();
  if (connected) {
    digitalWrite(WIFI_LED, HIGH);  // LED ثابت روشن
    sendGETRequest("/get_national_ids");
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

  nationalIdsJson = defaultIds;
  parseNationalIds(nationalIdsJson);
  return false;                       // هیچ شبکه‌ای وصل نشد
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
