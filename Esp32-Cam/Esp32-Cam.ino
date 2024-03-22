/*
--  Filename : Esp32-Cam-ino
--  Author : ECE492-RMC Group
--  Date : 06-Oct-2023
--  Design Name: Room control system satelite device firmware
--  Project Name: Room monitor and control
*
*   Acknowledgment (used libraries): 
*       ArduinoJson by Benoit Blanchon
*       PubSubClient by Nick O'Leary
*       ESP-32 QRcode scanner at: https://github.com/alvarowolfx/ESP32QRCodeReader
*
*/

#include "esp_camera.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h> //ArduinoJSON6
#include <Wire.h> //I2C library
DynamicJsonDocument CONFIG(2048);

//QRCode
#include <Arduino.h>
#include <ESP32QRCodeReader.h>

#include <string.h>

ESP32QRCodeReader reader(CAMERA_MODEL_AI_THINKER, FRAMESIZE_VGA);

char ssid[30];
char password[30];
//const char* ssid = "ece492_test";
//const char* password = "ETLCE3011xxt";
//const char* ssid = "testDesktop";
//const char* password = "12345678";
char mqtt_server[16];
//const char* mqtt_server = "192.168.137.125";
const char* HostName = "ESP32CAM_MQTT_01";
const char* topic_PHOTO = "TakeAPicture";
const char* topic_CONFIG = "JSONConfig";
const char* topic_UP = "sensor/occupancy";
const char* topic_UP_Temp = "sensor/temperature";
const char* topic_UP_Humid = "sensor/humidity";
const char* mqttUser = "ece492";
const char* mqttPassword = "ece492";
WiFiClient espClient;
PubSubClient client(espClient);


const bool debug = true;
bool wifiValid = false;

struct HIH_data_t {
  double temp;
  double Humid;
};

HIH_data_t HIH_Get_Data;

byte fetch_humidity_temperature(unsigned int *p_H_dat, unsigned int *p_T_dat)
{
      byte address, Hum_H, Hum_L, Temp_H, Temp_L, _status;
      unsigned int H_dat, T_dat;
      address = 0x27;
      Wire.beginTransmission(address); 
      Wire.endTransmission();
      delay(100);
      
      Wire.requestFrom((int)address, (int) 4);
      Hum_H = Wire.read();
      Hum_L = Wire.read();
      Temp_H = Wire.read();
      Temp_L = Wire.read();
      Wire.endTransmission();
      
      _status = (Hum_H >> 6) & 0x03;
      Hum_H = Hum_H & 0x3f;
      H_dat = (((unsigned int)Hum_H) << 8) | Hum_L;
      T_dat = (((unsigned int)Temp_H) << 8) | Temp_L;
      T_dat = T_dat / 4;
      *p_H_dat = H_dat;
      *p_T_dat = T_dat;
      return(_status);
}

void print_float(float f, int num_digits)
{
    int f_int;
    int pows_of_ten[4] = {1, 10, 100, 1000};
    int multiplier, whole, fract, d, n;

    multiplier = pows_of_ten[num_digits];
    if (f < 0.0)
    {
        f = -f;
        Serial.print("-");
    }
    whole = (int) f;
    fract = (int) (multiplier * (f - (float)whole));

    Serial.print(whole);
    Serial.print(".");

    for (n=num_digits-1; n>=0; n--) // print each digit with no leading zero suppression
    {
         d = fract / pows_of_ten[n];
         Serial.print(d);
         fract = fract % pows_of_ten[n];
    }
}

HIH_data_t get_HIH_data(){
  byte _status;
  unsigned int H_dat, T_dat;
  float RH, T_C;

  HIH_data_t HIH_data;
   
  _status = fetch_humidity_temperature(&H_dat, &T_dat);
    
  switch(_status)
  {
    case 0:  Serial.println("Normal.");
      break;
    case 1:  Serial.println("Stale Data.");
      break;
    case 2:  Serial.println("In command mode.");
      break;
    default: Serial.println("Diagnostic."); 
      break; 
  }       
  
  RH = (float) H_dat * 6.10e-3;
  T_C = (float) T_dat * 1.007e-2 - 40.0;

  print_float(RH, 1);
  Serial.print("  ");
  print_float(T_C, 2);
  Serial.println();
  // delay(1000);

  HIH_data.temp = T_C;
  HIH_data.Humid = RH;
  return HIH_data;
}


void callback(String topic, byte* message, unsigned int length) {
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }
  if (topic == topic_PHOTO) {
    Serial.println("PING");
    take_picture();
  }
  if (topic == topic_CONFIG) {
    deserializeJson(CONFIG, messageTemp);
    Serial.println(messageTemp);
    sensor_t * s = esp_camera_sensor_get();
    s->set_framesize(s, FRAMESIZE_VGA); //QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    s->set_vflip(s, CONFIG["vflip"]); //0 - 1
    s->set_hmirror(s, CONFIG["hmirror"]); //0 - 1
    s->set_colorbar(s, CONFIG["colorbar"]); //0 - 1
    s->set_special_effect(s, CONFIG["special_effect"]); // 0 - 6
    s->set_quality(s, CONFIG["quality"]); // 0 - 63
    s->set_brightness(s, CONFIG["brightness"]); // -2 - 2
    s->set_contrast(s, CONFIG["contrast"]); // -2 - 2
    s->set_saturation(s, CONFIG["saturation"]); // -2 - 2
    s->set_sharpness(s, CONFIG["sharpness"]); // -2 - 2
    s->set_denoise(s, CONFIG["denoise"]); // 0 - 1
    s->set_awb_gain(s, CONFIG["awb_gain"]); // 0 - 1
    s->set_wb_mode(s, CONFIG["wb_mode"]); // 0 - 4
  }
}

void camera_init() {
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = 5;
  config.pin_d1       = 18;
  config.pin_d2       = 19;
  config.pin_d3       = 21;
  config.pin_d4       = 36;
  config.pin_d5       = 39;
  config.pin_d6       = 34;
  config.pin_d7       = 35;
  config.pin_xclk     = 0;
  config.pin_pclk     = 22;
  config.pin_vsync    = 25;
  config.pin_href     = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn     = 32;
  config.pin_reset    = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  //config.pixel_format = PIXFORMAT_GRAYSCALE;

  config.frame_size   = FRAMESIZE_SVGA; // QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
  config.jpeg_quality = 10;           
  config.fb_count     = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void camera_reconfig() {
   sensor_t * s = esp_camera_sensor_get();
    s->set_framesize(s, FRAMESIZE_VGA); //QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    s->set_quality(s, 10); // 10 - 63
    s->set_pixformat(s, PIXFORMAT_JPEG);
}

void take_picture() {
  camera_fb_t * fb = NULL;
  fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }
  if (MQTT_MAX_PACKET_SIZE == 128) {
    //SLOW MODE (increase MQTT_MAX_PACKET_SIZE)
    client.publish_P(topic_UP, fb->buf, fb->len, false);
  }
  else {
    //FAST MODE (increase MQTT_MAX_PACKET_SIZE)
    client.publish(topic_UP, fb->buf, fb->len, false);
  }
  delay(500);
  Serial.println("image sent");
  esp_camera_fb_return(fb);
}


void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.mode(WIFI_STA);
  WiFi.setHostname(HostName);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);
  }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect(HostName, mqttUser, mqttPassword)) {
      Serial.println("connected");
      client.subscribe(topic_PHOTO);
      client.subscribe(topic_CONFIG);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      delay(2000);
    }
  }
}

void HIH_sensor_init() {
  Wire.begin(14, 13); //custom designed pin definition for sensor (HS2_Data2, HS2_Data3)
  pinMode(2, OUTPUT);
  digitalWrite(2, HIGH); // this turns on the HIH7121
  delay(250);
  Serial.println("Sensor initiallized>>>>>>>>>>>>>>>>>>>>>>>>");  // just to be sure things are working
}

void send_HIH_Data () {
  char Temp[6];
  char Humid[6];

  dtostrf(HIH_Get_Data.temp, 6, 4, Temp);
  dtostrf(HIH_Get_Data.Humid, 6, 4, Humid);

  Temp[5] = '\0';
  Humid[5] = '\0';

  client.publish(topic_UP_Temp, Temp);
  client.publish(topic_UP_Humid, Humid);
}

void onQrCodeTask(void *pvParameters)
{
  struct QRCodeData qrCodeData;

  while (true)
  {
    if (reader.receiveQrCode(&qrCodeData, 100))
    {
      Serial.println("Found QRCode");
      if (qrCodeData.valid)
      {
        Serial.print("Payload: ");
        Serial.println((const char *)qrCodeData.payload);
        
        char str[50];

        strcpy(str, (const char *)qrCodeData.payload);
        // Returns first token 
        char *token = strtok(str, " ");
        //copy to WIFI ssid
        strcpy(ssid, token);

        //copy to Wifi password
        token = strtok(NULL, " ");
        strcpy(password, token);

        //copy to broker id
        token = strtok(NULL, " ");
        strcpy(mqtt_server, token);

        wifiValid = true;
        vTaskDelete(NULL);
      }
      else
      {
        Serial.print("Invalid: ");
        Serial.println((const char *)qrCodeData.payload);
      }
    }
    vTaskDelay(100 / portTICK_PERIOD_MS);
  }
}

void setup() {
  Serial.begin(115200);

  Serial.println();
  reader.setup();
  Serial.println("Setup QRCode Reader");
  reader.beginOnCore(1);
  Serial.println("Begin on Core 1");
  xTaskCreate(onQrCodeTask, "onQrCode", 4 * 1024, NULL, 4, NULL);

  while(!wifiValid){
    delay(500);
  }

  camera_init();
  Serial.println(ESP.getHeapSize());
  Serial.println(ESP.getFreeHeap());
  Serial.println(ESP.getPsramSize());
  Serial.println(ESP.getFreePsram());
  HIH_sensor_init();
  get_HIH_data();

  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  client.setBufferSize(51200);
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  HIH_Get_Data = get_HIH_data();
  send_HIH_Data();
  take_picture();
  client.loop();
  delay(4500);
}