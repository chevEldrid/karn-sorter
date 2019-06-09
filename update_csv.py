import sys
import csv
import requests
import json
import time
#command line arguments: [-r] - just consolidate, no price pulling
#                        [-p] - just price, don't consolidate
card_file = "mtgcards.csv"
out_file = "mtgcards.csv"
cards = [] #name, qty, price
result_names = [] #list of result card names
result = [] #generated card list
#argv stuff
reprice = True
condense = True

def is_float(word):
    temp = False
    try:
        float(word)
        temp = True
    except:
        temp = False
    return temp

#given scryfall api card data, finds paper printing with cheapest price
def cheapest_print(cardData):
    printings = cardData["data"]
    prices = []
    for price in printings:
        cardPrice = price["prices"]["usd"]
        #if card has no usd price, it might only have a foil price
        if not is_float(cardPrice):
            cardPrice = price["prices"]["usd_foil"]
        if cardPrice != None:
            #print(printings[0]["name"] +": "+str(cardPrice))
            prices.append(float(cardPrice))
    return min(prices)

#given card name, pings scryfall for card data
def get_price(card):
    price = -1
    try:
        url = "https://api.scryfall.com/cards/search?q=!\"{0}\"&order={1}&unique=prints".format(card, "name")
        r = requests.get(url)
        x = json.loads(r.text)
        price = cheapest_print(x)
    except:
        print("ERROR ON: " + card)
    time.sleep(.1)
    return price

#---------------------------
#check for arg about repricing list
if '-r' in sys.argv:
    reprice = False
    print("Will not pull new price data from scryfall")
else:
    print("Will pull new price data from scryfall")
#check for arg about condensing list
if '-p' in sys.argv:
    condense = False
    print("Will not check for consolidation")
else:
    print("Will consolidate all duplicates")


#bring in file with all card information...
with open(card_file) as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        cards.append((row[0], row[1], row[2]))
#create copy of cards list to iterate through and not mess up for loop
del cards[0]
#sort for duplicates
for i, val in enumerate(cards):
    name = val[0]
    qty = int(val[1])
    old_price = val[2]
    #if the card hasn't already been found...
    if name not in result_names:
        if reprice:
            price = get_price(name)
        else:
            price = val[2]
        #iterate through every remaining entry in table, if condensing
        if condense:
            for j in range(i+1, len(cards)):
                if cards[j][0] == name:
                    qty += int(cards[j][1])
        #if there was an error with the price pulling...
        if float(price) > 0:
            result.append((name, qty, price))
            #if there's been a considerable change in price...
            if float(price) > 1.5*float(old_price):
                print("price spike on: {0}. From ${1} to ${2}".format(name, old_price, price))
            if float(price) < 0.5*float(old_price):
                print("price drop on: {0}. From ${1} to ${2}".format(name, old_price, price))
        else:
            result.append((name, qty, old_price, "FAILED"))
        #only add result to result name table if we're preventing duplicate searches
        if condense:
            result_names.append(name)
#now print to csv
with open(out_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["card","qty","price"])
    for card in result:
        writer.writerow([card[0], card[1], card[2]])
