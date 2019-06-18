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
#pricing info
bulk_ceiling = 0.99
bulk_rate = 5 #x$/1000 bulk cards
total_value = 0.0
bulk_count = 0

def is_float(word):
    temp = False
    try:
        float(word)
        temp = True
    except:
        temp = False
    return temp

#given scryfall api card data, finds paper printing with cheapest price
def cheapest_print(cardData, foil, set_code):
    printings = cardData["data"]
    prices = []
    for price in printings:
        #if foil flag, use foil price
        if foil:
            cardPrice = price["prices"]["usd_foil"]
        else:
            cardPrice = price["prices"]["usd"]
        #if card has no usd price, it might only have a foil price
        if not is_float(cardPrice):
            cardPrice = price["prices"]["usd_foil"]
        if cardPrice != None:
            #if specific set wanted, checked here
            if set_code == "":
                prices.append(float(cardPrice))
            else:
                if price["set"].upper() == set_code.upper():
                    prices.append(float(cardPrice))
    return min(prices)

#given card name, pings scryfall for card data
def get_price(card, foil, set_code):
    price = -1
    card_name = get_name(card)
    try:
        url = "https://api.scryfall.com/cards/search?q=!\"{0}\"&order={1}&unique=prints".format(card_name, "name")
        r = requests.get(url)
        x = json.loads(r.text)
        #pass foil flag to cheapest print
        price = cheapest_print(x, foil, set_code)
    except:
        print("ERROR ON: " + card)
    time.sleep(.1)
    return price

#given card name, is the card foil
def is_foil(card):
    words = card.split()
    for word in words:
        if word == "*f*":
            return True
    return False

#given card name, gets set code
def get_set_code(card):
    words = card.split()
    for word in words:
        if "[" in word:
            return word[1:-1]
    return ""

#removes tags given to card name on sheet
def get_name(card):
    words = card.split()
    name = []
    for word in words:
        #if card is foil...
        if word == "*f*":
            continue
        #if card has set code in the form [kld]...
        if "[" in word:
            continue
        name.append(word)
    return " ".join(name)
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
        try:
            cards.append((row[0], row[1], row[2]))
        except:
            print("Error on {0}. Will be dropped from Table".format(row[0]))
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
            foil = is_foil(name)
            set_code = get_set_code(name)
            price = get_price(name, foil, set_code)
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
            #different conditions if price is sub dollar
            if float(old_price) > 1.0:
                if float(price) > 1.15*float(old_price):
                    print("price spike on: {0}: From ${1} to ${2}".format(name, old_price, price))
                if float(price) < 0.85*float(old_price):
                    print("price drop on: {0}: From ${1} to ${2}".format(name, old_price, price))
            else:
                if float(price) > 1.5*float(old_price):
                    print("price spike on: {0}: From ${1} to ${2}".format(name, old_price, price))
        else:
            result.append((name, qty, old_price))
        #only add result to result name table if we're preventing duplicate searches
        if condense:
            result_names.append(name)
#sort prices from high to low
result = sorted(result, key=lambda tup: float(tup[2]), reverse=True)
#now print to csv
with open(out_file, "w") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["card","qty","price"])
    for card in result:
        #generate pricing info...
        if float(card[2]) > bulk_ceiling:
            total_value += (float(card[2]) * int(card[1])) #price * qty
        else:
            bulk_count += int(card[1]) #qty
        writer.writerow([card[0], card[1], card[2]])
collection_value = total_value + (bulk_count/1000.0*bulk_rate)
print("Total collection valued at {0:.2f}, with bulk rated at {1} per thousand".format(collection_value, bulk_rate))
