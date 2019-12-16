
import paho.mqtt.client as paho
import os
import socket
import ssl
from time import sleep
from random import uniform

connflag = False


def on_connect(client, userdata, flags, rc):  # func for making connection
    global connflag
    print("Connected to AWS")
    connflag = True
    print("Connection returned result: " + str(rc))


def on_message(client, userdata, msg):  # Func for Sending msg
    print(msg.topic + " " + str(msg.payload))


# def on_log(client, userdata, level, buf):
#    print(msg.topic+" "+str(msg.payload))

mqttc = paho.Client()  # mqttc object
mqttc.on_connect = on_connect  # assign on_connect func
mqttc.on_message = on_message  # assign on_message func
# mqttc.on_log = on_log

#### Change following parameters ####
awshost = "a1hvrmjbeiu1pl-ats.iot.us-east-2.amazonaws.com"
awsport = 8883
cliendId = "pid01"
thingName = "pid01"
caPath = "root-CA.crt"
certPath = "pid01.cert.pem"
keyPath = "pid01.private.key"  # <Thing_Name>.private.key

mqttc.tls_set(caPath, certfile=certPath, keyfile=keyPath, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2,
              ciphers=None)  # pass parameters

mqttc.connect(awshost, awsport, keepalive=60)  # connect to aws server

mqttc.loop_start()  # Start the loop

while 1 == 1:
    if connflag == True:
        tempreading = uniform(20.0, 25.0)  # Generating Temperature Readings
        mqttc.publish("temperature", tempreading, qos=1)  # topic: temperature # Publishing Temperature values
        print("msg sent: temperature " + "%.2f" % tempreading)  # Print sent temperature msg on console
        sleep(2)
    else:
        print("waiting for connection...")
