import sys
import csv
import requests
import json
import time
#command line arguments: [-r] - just consolidate, no price pulling
card_file = "mtgcards.csv"
out_file = "mtgcards.csv"
cards = [] #name, qty, price
result_names = [] #list of result card names
result = [] #generated card list
reprice = True

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
    cardPrice = price["prices"]["usd"]
    #if card has no usd price, it might only have a foil price
    if not is_float(cardPrice):
        cardPrice = price["prices"]["usd_foil"]
    if cardPrice != None:
        prices.append(cardPrice)
    return min(prices)

#given card name, pings scryfall for card data
def get_price(card):
    price = -1
    try:
        url = "https://api.scryfall.com/cards/search?q=!\"{0}\"&order={1}".format(card, name)
        r = requests.get(url)
        x = json.loads(r.text)
        price = cheapest_print(x)
    except:
        print("ERROR ON: " + card)
    time.sleep(.1)
    return price

#---------------------------
#check for arg about repricing list
try:
    if sys.argv[1] == "-r":
        reprice = False
        print("will not pull new price data from scryfall")
except:
    print("will consolidate and pull new prices from scryfall")

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
        #iterate through every remaining entry in table
        for j in range(i+1, len(cards)):
            if cards[j][0] == name:
                qty += 1
        #if there was an error with the price pulling...
        if float(price) > 0:
            result.append((name, qty, price))
            #if there's been a considerable change in price...
            if float(price) > 2*float(old_price):
                print("price spike on: {0}. From ${1} to ${2}".format(name, old_price, price))
        else:
            result.append((name, qty, old_price))
        result_names.append(name)
#now print to csv
with open(out_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["card","qty","price"])
    for card in result:
        writer.writerow([card[0], card[1], card[2]])
