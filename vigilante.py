#!/usr/bin/python
# Playing with a PIR motion sensor and the RaspberryPi Camera
# to detect unwanted visitors to the room


'''
+-----------------------------------------------------+
| +------------------------------------------------+  |
| | +-------------------------------------------+  |  |
| | |    +-----------------------------------+  |  |  |
| | |    |                       5v          |  |  |  |
| | |    | +---+                 |           |  |  |  |
| | |    | |   |  GPIO0       +--+--+        |  |  |  |
| | |    + | R +--------------+ PIR |        |  |  |  |
| | | GPIO1| A |              +--+--+        |  |  |  |
| | |      | S |                 |           |  |  |  |
| | ++GPIO2| P |              +--+-------+   |  |  |  |
| |        | B |              | GND      |   |  |  |  |  5v
| +--+GPIO3| E |              ++--+--+--++   |  |  |  |  +
|          | R |               |  |  |  |    |  |  |  |  |
+----+GPIO4| R |               +  +  +  +    +  +  +  +  +
           | Y |               1  3  5  16   11 12 13 14 15
           |   |   Tx         +---------------------------+
           |   +---------+    |                           |
           |   |         |    |           LCD1602         |
           |   |   Rx    |    |                           |
           |   +------+  |    +---------------------------+
           |   |      |  |     2   4  6
           |   |      |  |     +   +  +
           +---+      |  |     |   |  |
                      |  |     +   |  |
                      |  |   5v    |  |
                      |  |         |  |
                      |  +---------+  |
                      |               |
                      +---------------+

----------
PIR SENSOR
----------

       PRESET POTS
       +---+ +---+
       | X | | X |
+------+---+-+---+--------------+
|                               +-->
|                               |-->
|                       +--+    +-->
|                       |  |    |
|                       |  |    |
|                       |  |    |
|  +---+                |  |    |
|  +---+                +--+    |
|                               |
+-----------+-+-+---------------+
            | | |
            | | |
            v v v
          +5     GND
             OUT

'''

# AWS S3 boto3 (https://github.com/boto/boto3)
# 1 - set up credentials (in e.g. ~/.aws/credentials):
# 	[default]
# 	aws_access_key_id = YOUR_KEY
# 	aws_secret_access_key = YOUR_SECRET
# 2 - set up a default region (in e.g. ~/.aws/config):
# 	[default]
# 	region=eu-west-1

# Instructions:
# 	- source .env
# 	- (sudo -E) python vigilante.py

import RPi.GPIO as GPIO
import time
import picamera
import datetime
import sendgrid
import os
import boto3
from sendgrid.helpers.mail import *
from time import sleep
from lcd import LCD

# Main variables
sensorPin = 11
pin_rs = 8
pin_e = 10
pins_db = [12, 13, 15,16]
videoDuration = 5 # seconds
cam = picamera.PiCamera()
s3 = boto3.resource('s3')
prevState = False
currState = False
s3BucketName = os.environ.get('s3BucketName')
s3URL = os.environ.get('s3URL')
sendGrid = sendgrid.SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
lcd = None

def setup():
    global lcd
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(sensorPin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(pin_e, GPIO.OUT)
    GPIO.setup(pin_rs, GPIO.OUT)
    for pin in pins_db:
        GPIO.setup(pin, GPIO.OUT)
    lcd = LCD(pin_rs, pin_e, pins_db,GPIO)

def enableSystem():
    global lcd
    lcd.clear()
    lcd.message("VIGILANTE\nENABLED")

def getFileName():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H.%M.%S.h264")

def send_email(fileName):
    global s3BucketName,s3URL,sendGrid,lcd
    from_email = Email(os.environ.get('FROM_EMAIL'))
    subject = "Motion detected"
    to_email = Email(os.environ.get('TO_EMAIL'))
    video_link = s3URL + s3BucketName + "/" + fileName
    content = Content("text/plain", "Motion detected. Check video file at " + video_link)
    mail = Mail(from_email, subject, to_email, content)
    try:
        response = sendGrid.client.mail.send.post(request_body=mail.get())
        lcd.clear()
        lcd.message("Email notification\nsent")
    except Exception as e:
        lcd.clear()
        lcd.message("Error sending\nthe email")

def upload_video_to_s3(fileName):
    global lcd
    lcd.clear()
    lcd.message("Uploading\nvideo...")
    data = open(fileName, 'rb')
    try:
        s3.Bucket(s3BucketName).put_object(Key=fileName, Body=data)
        lcd.clear()
        lcd.message("Video uploaded\nsuccessfully")
        os.remove(fileName)
    except Exception as e:
        lcd.clear()
        lcd.message("Error uploading\nvideo")

def destroy():
    GPIO.cleanup()

def loop():
    global currState,prevState,lcd
    while True:
        time.sleep(.1)
        prevState = currState
        currState = GPIO.input(sensorPin)
        if currState != prevState:
            if currState:
                fileName = getFileName()
                cam.vflip = True
                cam.hflip = True
                cam.start_recording(fileName)
                lcd.clear()
                lcd.message("Motion detected\nRecording ...")
                sleep(videoDuration)
                cam.stop_recording()
                upload_video_to_s3(fileName)
                send_email(fileName)
                enableSystem()

if __name__ == '__main__':     # Program start from here
    setup()
    enableSystem()
    try:
        loop()
    except KeyboardInterrupt:  # 'Ctrl+C' pressed
        destroy()
