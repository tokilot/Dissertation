#include <ESP8266WiFi.h>
#include <WiFiManager.h>
#include <EEPROM.h>


//Wifi ssid and password, server host ip and port
const char* ssid = "NOKIA-90A1";
const char* password = "nDHyMaK9aB";

char mqtt_host[40];
char mqtt_port[6] = "1234";
char frequency[6] = "1000";//sample period  1000msec
char point[6] = "300";//sample size 5mins
char delaytime[6] = "1000";

//esp8266 AP static-ip, gateway and subnet
IPAddress AP_ip(192, 168, 18, 20);
IPAddress AP_gateway(192, 168, 0, 1);
IPAddress AP_subnet(255, 255, 255, 0);

WiFiServer server(80);  //端口号，随意修改，范围0-65535

//set input and output channels
int ledPin = 2;
int inPirPin = 0;
int outPirPin = 3;

unsigned long in_start_time;
unsigned long out_start_time;
int in_back;
int out_back;


//define function
void ConnectWifi();
void Light();
String SensorData();
String ReceiveIndex();

String mes;
String data;
int i=0;


void setup() {
  Serial.begin(9600);
  pinMode(inPirPin,INPUT);
  pinMode(outPirPin,INPUT);
  pinMode(ledPin,OUTPUT);

  Light(5000);

  //connect wifi and start server
  ConnectWifi();
  server.begin();
  Serial.printf("Web server started, open %s to communicate with ESP8266\n", WiFi.localIP().toString().c_str());
  Serial.println(WiFi.localIP());//输出板子的ip
}

void loop() {

  //connect Server and send the data
  WiFiClient client;
  int port = String(mqtt_port).toInt();
  int fre = String(frequency).toInt();
  int size = String(point).toInt();
  int delayed = String(delaytime).toInt();

  while(!client.connect(mqtt_host,port) && i<=10){
    Light(1000);
    i = i+1;
  }
  if(i > 10){
    return;
  }

  mes = "Test Message: Connecting to " + String(mqtt_host) + ". The client ip is " + client.localIP().toString();
  client.print(mes);
  Light(1000);
  mes = "This time the frequency is " + String(fre/1000) + " per point. Data will be collected in " + String(size) + " secs";
  client.print(mes);
  Light(1000);

  i = 0;

  while(client.connected() && (i*fre/1000)<size){
    data = SensorData(delayed);
    client.print(data);
    i = i+1;
    delay(fre);
  }
}


void ConnectWifi() 
{
  //connect wifi if saved, or return the wifimanager page;
  WiFiManager wifiManager;

  //custom parameters in wifimanager
  WiFiManagerParameter custom_mqtt_host("host", "Server Host", mqtt_host, 40);
  wifiManager.addParameter(&custom_mqtt_host);
  WiFiManagerParameter custom_mqtt_port("port", "Server Port", mqtt_port, 6);
  wifiManager.addParameter(&custom_mqtt_port);
  WiFiManagerParameter custom_frequency("frequency", "Frequency (Unit:msec)", frequency, 6);
  wifiManager.addParameter(&custom_frequency);
  WiFiManagerParameter custom_point("point", "Point (Unit:point)", point, 6);
  wifiManager.addParameter(&custom_point);
  WiFiManagerParameter custom_delaytime("delaytime", "Delaytime (Unit:msec)", delaytime, 6);
  wifiManager.addParameter(&custom_delaytime);

  wifiManager.startConfigPortal("Wifi-Esp8266","88888888");
  Serial.println("");
  Serial.println("WiFi connected");
  Light(1000);

  //get the value from wifimanager if user blank in
  strcpy(mqtt_host, custom_mqtt_host.getValue());
  strcpy(mqtt_port, custom_mqtt_port.getValue());
  strcpy(frequency, custom_frequency.getValue());
  strcpy(point, custom_point.getValue());
  strcpy(delaytime, custom_delaytime.getValue());

}

void Light(int time)
{
  //keep the led lighting for "time" milsecs;
  digitalWrite(ledPin,LOW);
  delay(time);
  digitalWrite(ledPin,HIGH);
}

String SensorData(int delayed)
{
  // read information from pir sensors and simply deal with information
  int in_state = digitalRead(inPirPin);
  int out_state = digitalRead(outPirPin);

  if((millis()-in_start_time)<delayed){
    in_state = 1;
  }
  if(in_state==1 && in_back==0){
    in_start_time = millis();
  }
  in_back = in_state;

  if((millis()-out_start_time)<delayed){
    out_state = 1;
  }
  if(out_state==1 && out_back==0){
    out_start_time = millis();
  }
  out_back = out_state;

  String res = String(in_back) + String(out_back);
  return res;
}


