import sys
import os
card_lists = ["cards.txt", "prices.txt"]
PRG_PATH = "/home/pi/karn-sorter"
FOLDER = "test"
#clears cards.txt and prices.txt for testing purposes
for l in card_lists:
    with open(l, "w") as myfile:
        myfile.write("")
print "storage files cleared!"
for filename in os.listdir(PRG_PATH+'/'+FOLDER):
    os.remove(filename)
print "card pictures cleared!"
