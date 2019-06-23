import sys
import os
import csv
#card_lists = ["cards.txt"]
#card_sheets = ["mtgcards.csv"]
card_lists = []
card_sheets = []
PRG_PATH = "/home/pi/karn-sorter"
FOLDER = "test"
CP_FOLDER = "crops"

input = input("This script will clear all stored card lists AND delete all card photos in " + PRG_PATH+"/"+FOLDER+"...type [y]es to continue:  ")

if input == "y":
    #clears cards.txt for testing purposes
    for l in card_lists:
        with open(l, "w") as myfile:
            myfile.write("")
    for s in card_sheets:
        with open(s, "w") as myfile:
            writer = csv.writer(myfile)
            writer.writerow(["card","qty", "price"])

    print("storage files cleared!")
    for filename in os.listdir(PRG_PATH+'/'+FOLDER):
        os.remove(FOLDER + "/" + filename)
    print("card pictures cleared from local directory!")
    #removes any leftovers from the crops directory (if you ran cam_setup.py)
    for filename in os.listdir(PRG_PATH+'/'+CP_FOLDER):
        os.remove(CP_FOLDER + "/" + filename)
    print("crop tests removed from /"+CP_FOLDER)
else:
    print("input not recognized. try again!")
