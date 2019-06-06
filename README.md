# karn-sorter
An automatic mtg card identifier using a raspberry pi and amazon rekognition to catalog cards by price

Using mostly pieces from a lego mindstorm kit to construct the frame (and a few random supports from an old LEGO Exoforce set..) I've rigged up a Raspberry Pi connected to a camera focused through three lenses, and a servo to control card drops.

Each picture is then cropped to include just the card title, sent to AWS for image->word analysis, and finally run through Scryfall's api for price data that's saved in a .csv. If no match is made for the card name (Rekognition mistakes a 't' for an 'f'), a second picture is taken and uploaded. This process will occur five times without human interaction and this greatly increases the success rate per card.

four scripts are currently included in this repo:
sort_lookup.py -> runs the card reader doing the aws and scryfall calls
cam_setup.py -> takes multiple photos with various croppings to see which includes card's entire title block
clear_lists.py -> clears local pictures and cards.txt, which stores the card names of cards scanned
update_csv.py -> runs on output of sort_lookup to condense multiple copies of same card and update card prices according to scryfall

[Project Page](https://www.hackster.io/chev-eldrid/magic-the-gathering-card-pricer-a5e819)
