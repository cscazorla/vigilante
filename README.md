# Vigilante
A surveillance system based on RaspberryPi + LCD1602 + PIR Sensor + Camera to detect unwanted visitors to the room

```
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
```

## Requirements
- Setup a Sendgrid account and an API key in order to send emails
- Boto3 (https://github.com/boto/boto3) as videos are uploaded to AWS S3.

## Installation
- Install all dependencies
```
pip install
```
- Set up AWS Credentials (~/.aws/credentials):
```
[default]
 aws_access_key_id = YOUR_KEY
 aws_secret_access_key = YOUR_SECRET
```
- Set up a default AWS region for the S3 bucket (~/.aws/config):
```
[default]
 region=eu-west-1
```
- Copy .env.example to .env, fill it and source it
```
source .env
```
- Run vigilante
```
sudo -E python vigilante.py
```

## To do
- Use https://github.com/theskumar/python-dotenv to read key,value from .env
