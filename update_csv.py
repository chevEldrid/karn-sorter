import csv

card_file = "mtgcards.csv"
out_file = "cardlist.csv"
cards = [] #name, qty, price
result_names = [] #list of result card names
result = [] #generated card list
#---------------------------
#read in file with all card information...
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
    price = val[2]
    #if the card hasn't already been found...
    if name not in result_names:
        #iterate through every remaining entry in table
        for j in range(i+1, len(cards)):
            if cards[j][0] == name:
                qty += 1
        result.append((name, qty, price))
        result_names.append(name)
#now print to csv
with open(out_file, "wb") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["card","qty","price"])
    for card in result:
        writer.writerow([card[0], card[1], card[2]])
