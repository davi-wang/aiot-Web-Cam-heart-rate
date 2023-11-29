#include <WiFiClientSecure.h>
#include <MQTTClient.h>
#include "WiFi.h"
#include "esp_camera.h"
#define CAMERA_MODEL_WROVER_KIT
#include "camera_pins.h"
 // Has PSRAM
// #define PWDN_GPIO_NUM     32
// #define RESET_GPIO_NUM    -1
// #define XCLK_GPIO_NUM      0
// #define SIOD_GPIO_NUM     26
// #define SIOC_GPIO_NUM     27
// #define Y9_GPIO_NUM       35
// #define Y8_GPIO_NUM       34
// #define Y7_GPIO_NUM       39
// #define Y6_GPIO_NUM       36
// #define Y5_GPIO_NUM       21
// #define Y4_GPIO_NUM       19
// #define Y3_GPIO_NUM       18
// #define Y2_GPIO_NUM        5
// #define VSYNC_GPIO_NUM    25
// #define HREF_GPIO_NUM     23
// #define PCLK_GPIO_NUM     22

#define ESP32CAM_PUBLISH_TOPIC   "camera/image"

const char* mqtt_server = "18.163.181.228";
const int mqtt_port = 1883;
const char* mqtt_user = "admin"; // 如果需要用户名和密码认证
const char* mqtt_password = "HKUaiot7310";
const char* mqtt_topic = "camera/image"; // MQTT主题
const int bufferSize = 1024 * 23; // 23552 bytes
const char* ssid = "CAI";
const char* password = "12345678";
WiFiClient net= WiFiClient();
MQTTClient client = MQTTClient(bufferSize);

void connectAWS()
{
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);

  Serial.println("\n\n=====================");
  Serial.println("Connecting to Wi-Fi");
  Serial.println("=====================\n\n");

  while (WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  // Configure WiFiClientSecure to use the AWS IoT device credentials
//  net.setCACert(AWS_CERT_CA);
//  net.setCertificate(AWS_CERT_CRT);
//  net.setPrivateKey(AWS_CERT_PRIVATE);

  // Connect to the MQTT broker on the AWS endpoint we defined earlier
//  client.begin(AWS_IOT_ENDPOINT, 8883, net);
  client.begin(mqtt_server, mqtt_port, net);
  client.setCleanSession(true);

  Serial.println("\n\n=====================");
  Serial.println("Connecting to IOT");
  Serial.println("=====================\n\n");

  while (!client.connect("ESP32-CAM", mqtt_user, mqtt_password)) {
    Serial.print(".");
    delay(100);
  }

  if(!client.connected()){
    Serial.println("IoT Timeout!");
    ESP.restart();
    return;
  }

  Serial.println("\n\n=====================");
  Serial.println("IoT Connected!");
  Serial.println("=====================\n\n");
}

void cameraInit(){
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 40000000;;
  config.frame_size = FRAMESIZE_QVGA;
  config.pixel_format = PIXFORMAT_JPEG; // for streaming
  //config.pixel_format = PIXFORMAT_RGB565; // for face detection/recognition
  // config.grab_mode = CAMERA_GRAB_LATEST ;
  // config.fb_location = CAMERA_FB_IN_PSRAM;
  config.jpeg_quality = 10;
  config.fb_count = 1;
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    ESP.restart();
    return;
  }
}
unsigned long start_time;
unsigned long end_time;
void grabImage(){
  camera_fb_t * fb = esp_camera_fb_get();

  if(fb != NULL && fb->format == PIXFORMAT_JPEG && fb->len < bufferSize){
    Serial.print("Image Length: ");
    Serial.print(fb->len);
    Serial.print("\t Publish Image: ");
    start_time = millis();

    // int message = 1;

    // bool result = (client.publish(mqtt_topic, String(message).c_str()));
    bool result = client.publish(ESP32CAM_PUBLISH_TOPIC, (const char*)fb->buf, fb->len);
    end_time = millis();
    Serial.println(result);
    Serial.print("Delay : ");
    Serial.println(end_time-start_time);
    if(!result){
      ESP.restart();
    }
  }
  esp_camera_fb_return(fb);
  // delay(1);
}

void setup() {
  Serial.begin(115200);
  cameraInit();
  connectAWS();
}

void loop() {
  client.loop();
  if(client.connected()) grabImage();
}