from ebaysdk.finding import Connection as Finding
from ebaysdk.exception import ConnectionError
from pymongo import MongoClient
from email.message import EmailMessage
from dotenv import load_dotenv
import os
import time
import json
import smtplib

load_dotenv()

EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EBAY_APPID = os.getenv('EBAY_APPID')
MONGO_CONNECTION_STRING = os.getenv('MONGO_CONNECTION_STRING')

def send_notification(item, message):
    msg = EmailMessage()
    msg['Subject'] = "!!! NEW " + item + " LISTING !!!"
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = EMAIL_ADDRESS
    msg.set_content(message)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

try:
    api = Finding(appid=EBAY_APPID, config_file=None)
    response = api.execute('findItemsAdvanced', {'keywords': 'sony A7ii', 'sortOrder': 'StartTimeNewest'})
except ConnectionError as e: 
    print(e)
    print(e.response.dict())

parseSearch = json.loads(response.json())
results=parseSearch['searchResult']

def get_database():
   client = MongoClient(MONGO_CONNECTION_STRING)
   return client['Listings']

listings = get_database()
sonyA7iii = listings['sonyA7iii']

while(True):
    response = api.execute('findItemsAdvanced', {'keywords': 'sony A7iii', 'sortOrder': 'StartTimeNewest'})
    parseSearch = json.loads(response.json())
    results=parseSearch['searchResult']

    for i in results['item']:
        if i['listingInfo']['listingType'] == "Auction":
            continue
        price = i['sellingStatus']['convertedCurrentPrice']['value']
        if float(price) > 100:
            if bool(sonyA7iii.find_one({"_id": i['itemId']})) == True:
                break
            else:
                item = {
                    "_id": i['itemId'],
                    "name": i['title'],
                    "price": price,
                    "url": i['viewItemURL'],
                    "location": i['location'],
                    "listingType": i['listingInfo']['listingType'],
                    "bestOffer": i['listingInfo']['bestOfferEnabled']
                }
                print("!!!New Listing Added!!!")
                send_notification("SONY A7III", "Price: " + str(price) + "\nURL: " + i['viewItemURL'] + "\nListing Type: " + i['listingInfo']['listingType'])
                sonyA7iii.insert_one(item)
    print("Nothing yet...")
    time.sleep(10)