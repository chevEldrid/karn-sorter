from PIL import Image
from picamera import PiCamera
import RPi.GPIO as GPIO
import sys
import time

servoPin = 18
camera = PiCamera()
rotation_angle = 4
alignment_time = 5
#runtime arguements
manual_switch = False

def camera_setup(camera):
    #camera.color_effects = (128, 128)
    camera.rotation = 0
    camera.resolution = (1000, 1000)

def setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(servoPin, GPIO.OUT)

#argument parsing
print "Welcome to Karn Card Processor"
try:
    if sys.argv[1] == "-m":
        manual_switch  = True
        print "you have selected manual"
except:
    print "you have selected automatic."
    print "card will drop after " + str(alignment_time) + " seconds"

#use raw_input with python 2, input with python 3
raw_input("Press any button to begin...")
#program setup
setup()
camera_setup(camera)

pwm = GPIO.PWM(servoPin, 100)
pwm.start(5)

#now for the loop
while True:
    pwm.ChangeDutyCycle(0.5)
    print "You have 5 seconds to place card before picture: "
    time.sleep(alignment_time)
    print "Picture taking in process..."
    timestamp=time.strftime("%Y%m%d%H%M%S")
    pic_name = "test/mtg_"+timestamp+".jpg"
    camera.capture(pic_name)

    #crop photo to just card name
    img = Image.open(pic_name)
    print "attempting to crop..."
    area = (325, 520, 700, 620)
    cropped_img = img.crop(area)
    #cropped_img = cropped_img.rotate(rotation_angle)
    cropped_img.save(pic_name)

    print "Picture taken! See mtg_{0}.jpg!".format(timestamp)
    if manual_switch:
        raw_input("Press any button to drop card")
    pwm.ChangeDutyCycle(13.5)
    time.sleep(0.5)

GPIO.cleanup()
