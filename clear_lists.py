import sys
import os
card_lists = ["cards.txt", "prices.txt"]
PRG_PATH = "/home/pi/karn-sorter"
FOLDER = "test"
CP_FOLDER = "crops"

input = raw_input("This script will clear all stored card lists AND delete all card photos in " + PRG_PATH+"/"+FOLDER+"...type [y]es to continue:  ")

if input == "y":
    #clears cards.txt and prices.txt for testing purposes
    for l in card_lists:
        with open(l, "w") as myfile:
            myfile.write("")
    print "storage files cleared!"
    for filename in os.listdir(PRG_PATH+'/'+FOLDER):
        os.remove(FOLDER + "/" + filename)
    print "card pictures cleared from local directory!"
    #removes any leftovers from the crops directory (if you ran cam_setup.py)
    for filename in os.listdir(PRG_PATH+'/'+CP_FOLDER):
        os.remove(CP_FOLDER + "/" + filename)
    print "crop tests removed from /"+CP_FOLDER
else:
    print "input not recognized. try again!"
