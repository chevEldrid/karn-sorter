import sys
import csv
#Given a name and a file, deletes one instance of the card from that file or returns not found
#---------------------------

card_list = []
card_name = ""
list_result = []
found = False

def read_file(file):
	temp = []
	with open(file) as csvfile:
	    readCSV = csv.reader(csvfile, delimiter=',')
	    for row in readCSV:
	        try:
	            temp.append((row[0], row[1], row[2]))
	            #print(row)
	        except:
	            print("Error on {0}. Will be dropped from Table".format(row[0]))
	#create copy of cards list to iterate through and not mess up for loop
	del temp[0]
	return temp

try:
    with open(sys.argv[2]) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        print(sys.argv[2] + " successfully read in")
    print("Will delete one instance of "+sys.argv[1]+" in file")
except:
    print("ERROR: csv file could not be read. Please input name of csvs as second arg")
    sys.exit()

card_file = sys.argv[2]
card_name = sys.argv[1]

card_list = read_file(card_file)

for i, val in enumerate(card_list):
	name = val[0]
	qty = int(val[1])
	price = float(val[2])
	#if the card hasn't already been found...
	if not found and name == card_name:
		found = True
		if qty > 1:
			list_result.append((name, (qty - 1), price))
	else:
		list_result.append((name, qty, price))

if found:
	with open(card_file, "w") as csvfile:
	    writer = csv.writer(csvfile)
	    writer.writerow(["card","qty","price"])
	    for card in list_result:
	        writer.writerow([card[0], card[1], card[2]])
	print("SUCCESS: " +sys.argv[1]+" found successfully and one copy removed!")
else:
	print("ERROR: "+sys.argv[1] + " could not be found in the selected file...")