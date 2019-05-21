# karn-sorter
An automatic mtg card identifier using a raspberry pi and amazon rekognition to catalog cards by price

Using mostly pieces from a lego mindstorm kit to construct the frame (and a few random supports from an old LEGO Exoforce set..) I've rigged up a Raspberry Pi connected to a camera focused through two lenses, and a servo to control card drops. Pictures will be provided sometime soon. This code includes the card picture code in sort.py, and the connection to amazon in aws_list.py that outputs a list of cards scanned.

It's not as reliable as I'd like yet, so further tinkering is definitely in the immediate future. Generally sitting at an 8/10 for card -> listed name. 

Will also include the program for polling scryfall's db for price data on each individual card in a list (i.e. the output of aws_list.py)
