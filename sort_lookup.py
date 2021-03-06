from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import sys
import time
import csv
#imports for the aws portion
import boto3
import os
#imports for api lookup
import requests
import json

#system arguments: -f :use foiling pricing for all cards scanned this session
#pin on pi connected to servo control
servoPin = 18
camera = PiCamera()
#if cards are at an angle, use this to right them
rotation_angle = 0
#time given between pictures
alignment_time = 4
#time given between retriy pictures
retry_align_time = 2
#cropped area of photo
area = (325, 550, 700, 650)
#expanded area of photo cropped if first few pics don't work
ex_area = (300, 500, 750, 650)
#runtime arguments
auto_switch = False
#aws arguments
s3 = boto3.resource("s3")
PRG_PATH = "/home/pi/karn-sorter"
BUCKET = "mtg-cardnames"
FOLDER = "test"
card_name = ""
#api arguments
#general stuff
retry = 5
total_value = 0.0
#these numbers should match: starting count and total possible
max_retry = 5
#total cards scanned in this session
total_cards = 0
#total failures in this session
total_failures = 0
#if using foil prices for session
foil = False

cont = True

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
    if retry > max_retry/2:
        cropped_img = img.crop(area)
    else:
        cropped_img = img.crop(ex_area)
    #cropped_img = cropped_img.rotate(rotation_angle)
    cropped_img.save(pic_name)

#given picture name, uploads to S3 and runs against rekognition
def get_name(filename):
    card_name = ""
    s3.Bucket(BUCKET).upload_file(filename, filename)
    #print(filename + " successfully uploaded to S3")
    client = boto3.client('rekognition')
    response = client.detect_text(Image={'S3Object':{'Bucket':BUCKET, 'Name':filename}})
    textDetections=response['TextDetections']
    for text in textDetections:
        if text["Type"] == "LINE":
            if text['Confidence'] > 90.0:
               card_name = text['DetectedText']
               break
    return card_name

#catch method for some of the general errors from Rekognition
def clean_name(card):
    if card != '':
        card_words = card.split()
        words = []
        for word in card_words:
            #aws confuses new font "J" for "l"
            if(word[0] == "l"):
                word = "J"+word[1:]
            #sometimes "to" is confused with "10"
            if word == "10":
                word = "to"
            words.append(word)
        #sometimes it picks up generic mana symbols...
        if is_int(words[-1]):
            del card_words[-1]
        #rejoin all words
        card = ' '.join(words)
        #periods instead of commas
        card = card.replace(".",",")
    return card

#helper for number reading
def is_int(word):
    temp = False
    try:
        int(word)
        temp = True
    except:
        temp = False
        #code breaks trying to int(gorgonzola)
    return temp

def is_float(word):
    temp = False
    try:
        float(word)
        temp = True
    except:
        temp = False
    return temp

#given api card data, finds paper printing with lowest price
def cheapestPrint(cardData):
    printings = cardData["data"]
    prices = []
    for price in printings:
        cardPrice = price["prices"]["usd"]
        if foil:
            cardPrice = price["prices"]["usd_foil"]
        if not is_float(cardPrice):
            cardPrice = price["prices"]["usd_foil"]
        if cardPrice != None:
            prices.append(float(cardPrice))
    return min(prices)

#given a card name, pings Scryfall to see if a card exists with name and then price
def get_price(card):
    global retry
    price = -1
    try:
        url = "https://api.scryfall.com/cards/search?q=!\"{0}\"&order={1}&unique=prints".format(card, "name")
        r = requests.get(url)
        x = json.loads(r.text)
        price = cheapestPrint(x)
        print("cheapest price got")
        print(card + ": $" + str(price))
        add_value(price)
    except:
        print("ERROR")
        #basically a catch if card isn't found
    return price

#adds a card price to running total value
def add_value(price):
    global total_value
    total_value = total_value + float(price)

#deals with all possible actions after card read
#SIDE EFFECTS: moves servo
def cont_program(pwm, redo=False):
    while True:
        prompt = "Would you like to [c]ontinue or [q]uit?  "
        if redo:
            prompt = "Would you like to [c]ontinue, [q]uit, or [r]etry?  "
        resp  = input(prompt)
        if resp == "c":
            pwm.ChangeDutyCycle(13.5)
            time.sleep(0.5)
            return True
        elif resp == "q":
            return False
        elif resp == "r" and redo:
            return True
        else:
            print("Couldn't understand input, please respond only with c,q, or r.")
#----------------------------------------------------------------
#argument parsing
#auto next card
print("Welcome to Karn Card Processor 1.0")
if "-a" in sys.argv:
    auto_switch  = True
    print("you have selected automatic")
    print("card will drop after " + str(alignment_time) + " seconds")
else:
    print("you have selected manual.")
#use foil prices for session
if "-f" in sys.argv:
    foil = True
    print("Will use usd_foil prices for all cards scanned")

input("Press Enter to begin...")
#program setup
setup()
camera_setup(camera)

pwm = GPIO.PWM(servoPin, 100)
pwm.start(5)

#now for the loop
while True:
    pwm.ChangeDutyCycle(0.5)
    #speed things up if it's a retry of a previous card
    a_time = alignment_time
    if retry != max_retry:
        a_time = retry_align_time
    print("You have "+ str(a_time) +"  seconds to place card before picture: ")
    time.sleep(a_time)
    print("Picture taking in process...")
    timestamp=time.strftime("%Y%m%d%H%M%S")
    pic_name = "test/mtg_"+timestamp+".jpg"
    camera.capture(pic_name)
    #crop photo to just card name
    crop_picture(pic_name)
    #print("Picture taken! See {0}!".format(pic_name))
    #here's where all the new stuff goes...
    card = get_name(pic_name)
    card = clean_name(card)
    price = get_price(card)
    if float(price) > 0:
        #if price > 0, means card was found - so we can be more confident on name too
        #increase count of total cards scanned
        total_cards += 1
        #adds prices and names to a csv
        with open("mtgcards.csv", "a") as myfile:
            writer = csv.writer(myfile)
            if foil:
                card = card + " *f*"
            writer.writerow([card, "1", str(price)])
        print(card + " added to storage files")
        if not auto_switch:
            cont = cont_program(pwm)
        else:
            pwm.ChangeDutyCycle(13.5)
            time.sleep(0.5)
        retry = max_retry
    else:
        retry -= 1
        if retry > 0:
            print(card + " not found. Will retry " + str(retry) + " more times")
        else:
            print("Max number of retries reached.")
            retry = max_retry
            #increase total failure count
            total_failures += 1
            cont = cont_program(pwm, True)
    if not cont:
        str_value = ("%.2f" % total_value)
        str_sell = ("%.2f" % (total_value * 2 / 3))
        #show end of section in files...
        print("Total value of cards scanned is ${0}".format(str_value))
        print("Approx sell value of cards scanned is ${0}".format(str_sell))
        success_ratio = float(total_failures)/float(total_cards)*100
        print("Failure rate at: {0:.2f}%".format(success_ratio))
        print("Program exiting. Thank you!")
        break
GPIO.cleanup()
