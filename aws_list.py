import boto3
import os
import sys

s3 = boto3.resource("s3")
PRG_PATH = "/home/pi/karn-sorter"
BUCKET = "mtg-cardnames"
FOLDER = "test"
card_names = []
#uploads all files of given folder to s3 w/o folder prefix
for filename in os.listdir(PRG_PATH+'/'+FOLDER):
    s3.Bucket(BUCKET).upload_file(FOLDER+"/"+filename, filename)
print "pictures uploaded successfully! Attempting Text Recognition:"
#now for the rekognition part...
client = boto3.client('rekognition')
#okay we're gonna do something a little hacky..iterate over items
#in local directory bc they have same names as s3 bucket
for filename in os.listdir(PRG_PATH+'/'+FOLDER):
    response = client.detect_text(Image={'S3Object':{'Bucket':BUCKET, 'Name':filename}})
    textDetections=response['TextDetections']
    for text in textDetections:
        if text["Type"] == "LINE":
            if text["Confidence"] > 90.0:
                print('Detected Text:' + text['DetectedText'])
                card_names.append(text['DetectedText'])

#printing card names to text file
card_file = open("cards.txt", "w")
for cn in card_names:
    card_file.write(cn + "\n")
card_file.close()
print("card names saved to 'cards.txt'")
