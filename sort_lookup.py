from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import sys
import time
#imports for the aws portion
import boto3
import os
#imports for api lookup
import requests
import json

servoPin = 18
camera = PiCamera()
rotation_angle = 4
alignment_time = 5
#runtime arguments
manual_switch = False
#aws arguments
s3 = boto3.resource("s3")
PRG_PATH = "/home/pi/karn-sorter"
BUCKET = "mtg-cardnames"
FOLDER = "test"
card_name = ""
#api arguments
#general stuff
retry = 5

def camera_setup(camera):
    #camera.color_effects = (128, 128)
    camera.rotation = 0
    camera.resolution = (1000, 1000)

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(servoPin, GPIO.OUT)

#given picture name, crops it to just include name of card
def crop_picture(pic_name):
    img = Image.open(pic_name)
    area = (325, 515, 700, 600)
    cropped_img = img.crop(area)
    #cropped_img = cropped_img.rotate(rotation_angle)
    cropped_img.save(pic_name)

#given picture name, uploads to S3 and runs against rekognition
def get_name(filename):
    s3.Bucket(BUCKET).upload_file(filename, filename)
    print filename + " successfully uploaded to S3"
    client = boto3.client('rekognition')
    response = client.detect_text(Image={'S3Object':{'Bucket':BUCKET, 'Name':filename}})
    textDetections=response['TextDetections']
    for text in textDetections:
        if text["Type"] == "LINE":
            if text['Confidence'] > 90.0:
               card_name = text['DetectedText']
               break
    return card_name

#given api card data, finds paper printing with lowest price
def cheapestPrint(cardData):
    printings = cardData["data"]
    prices = []
    for price in printings:
        cardPrice = price["prices"]["usd"]
        if cardPrice != None:
            prices.append(cardPrice)
    return min(prices)

#given a card name, pings Scryfall to see if a card exists with name and then price
def get_price(card):
    global retry
    price = -1
    try:
        url_params = {'q':card, 'unique':'prints', 'order':'usd'}
        r = requests.get("https://api.scryfall.com/cards/search", params=url_params)
        x = json.loads(r.text)
        price = cheapestPrint(x)
        print card + ": $" + str(price)
    except:
        print "ERROR"
        #basically a catch if card isn't found
    return price

#argument parsing
print "Welcome to Karn Card Processor 1.0"
try:
    if sys.argv[1] == "-m":
        manual_switch  = True
        print "you have selected manual"
except:
    print "you have selected automatic."
    print "card will drop after " + str(alignment_time) + " seconds"

#use raw_input with python 2, input with python 3
raw_input("Press Enter to begin...")
#program setup
setup()
camera_setup(camera)

pwm = GPIO.PWM(servoPin, 100)
pwm.start(5)

#now for the loop
while True:
    pwm.ChangeDutyCycle(0.5)
    print "You have "+ str(alignment_time) +"  seconds to place card before picture: "
    time.sleep(alignment_time)
    print "Picture taking in process..."
    timestamp=time.strftime("%Y%m%d%H%M%S")
    pic_name = "test/mtg_"+timestamp+".jpg"
    camera.capture(pic_name)
    #crop photo to just card name
    crop_picture(pic_name)
    print "Picture taken! See {0}!".format(pic_name)
    #here's where all the new stuff goes...
    card = get_name(pic_name)
    price = get_price(card)
    if price > 0:
        #if price > 0, means card was found - so we can be more confident on name too
        #add card name to stored names file
        with open("cards.txt", "a") as myfile:
            myfile.write(card+"\n")
        with open("prices.txt", "a") as myfile:
            card_price = card + ": $" + str(price)
            myfile.write(card_price + "\n")

        print card + " added to storage files"
        if manual_switch:
            raw_input("Press Enter to drop card")
        pwm.ChangeDutyCycle(13.5)
        time.sleep(0.5)
        retry = 5
    else:
        retry -= 1
        if retry > 0:
            print card + "not found. Will retry " + str(retry) + " more times"
        else:
            print "Max number of retries reached. Moving on. Please insert new card"
            pwm.ChangeDutyCycle(13.5)
            time.sleep(0.5)

GPIO.cleanup()
