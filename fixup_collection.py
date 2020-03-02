import sys
import csv
#Given two csv files, moves all cards above one threshold to the first file, and all below to the other...
#---------------------------
#intake output file
BULK_CEILING = 0.99
valued = []
bulk = []
valued_result = []
bulk_result = []

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

def sort_list(card_list):
	for i, val in enumerate(card_list):
	    name = val[0]
	    qty = val[1]
	    price = float(val[2])
	    #if the card hasn't already been found...
	    if price > BULK_CEILING:
	    	valued_result.append((name, qty, price))
	    else:
	    	bulk_result.append((name, qty, price))

def write_to_file(file, output_list):
	with open(file, "w") as csvfile:
	    writer = csv.writer(csvfile)
	    writer.writerow(["card","qty","price"])
	    for card in output_list:
	        writer.writerow([card[0], card[1], card[2]])

try:
    with open(sys.argv[1]) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        print(sys.argv[1] + " successfully read in, value will be stored here.")
    with open(sys.argv[2]) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        print(sys.argv[2] + " successfully read in, bulk will be stored here.")
except:
    print("ERROR: csv files could not be read. Please input names of csvs as first and second arg")
    sys.exit()

valued_file = sys.argv[1]
bulk_file = sys.argv[2]

valued = read_file(valued_file)
bulk = read_file(bulk_file)

sort_list(valued)
sort_list(bulk)

#sort prices from high to low
valued_result = sorted(valued_result, key=lambda tup: float(tup[2]), reverse=True)
bulk_result = sorted(bulk_result, key=lambda tup: float(tup[2]), reverse=True)
#now print to csv
write_to_file(valued_file, valued_result)
write_to_file(bulk_file, bulk_result)

print("Bulk successfully sorted. Have a pleasant day")
