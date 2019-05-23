import sys
card_lists = ["cards.txt", "prices.txt"]
#clears cards.txt and prices.txt for testing purposes
for l in card_lists:
    with open(l, "w") as myfile:
        myfile.write("")
print "files cleared!"
