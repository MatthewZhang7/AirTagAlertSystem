import os
from twilio.rest import Client
from dotenv import load_dotenv
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from time import sleep

load_dotenv()
MONGO_URI = os.environ["MONGODB_URI"]

# Connect to MongoDB
def connect_to_mongo():
    try:
        client = MongoClient(MONGO_URI)
        db = client['airtag_db']
        collection = db['locations']
        return collection
    except ServerSelectionTimeoutError:
        print('Error: Unable to connect to MongoDB')
        return None

# Check geofence status of the most recent record
def check_geofence(collection):
    latest_record = collection.find().sort("datetime", -1).limit(1)
    latest_record = list(latest_record)  # Convert cursor to list
    if latest_record:
        geofence_status = latest_record[0].get("is_within_geofence", None)
        print(f"Geofence status: {geofence_status}")
        print(f"Latest record: {latest_record[0]}")
        return geofence_status
    else:
        print("No records found in the database.")
        return None

# Make a Twilio call
def make_call():
    try:
        account_sid = os.environ["ACCOUNT_SID"]
        auth_token = os.environ["AUTH_TOKEN"]
        to_phone_number = os.environ["TO_PHONE_NUMBER"]
        from_phone_number = os.environ["FROM_PHONE_NUMBER"]
        client = Client(account_sid, auth_token)

        call = client.calls.create(
            twiml="<Response><Say>The geofence has been breached.</Say></Response>",
            to=to_phone_number,
            from_=from_phone_number,
        )
        print(f"Call initiated. SID: {call.sid}")
    except Exception as e:
        print(f"Error making call: {e}")

if __name__ == "__main__":
    collection = connect_to_mongo()
    if collection is None:
        print("Failed to connect to MongoDB. Exiting...")
        exit(1)

    print("Connected to MongoDB")
    LAST_GEOFENCE_STATUS = True  

    while collection is not None:
        geofence_status = check_geofence(collection)
        if geofence_status == False and LAST_GEOFENCE_STATUS == True:
            print("Triggering alert call due to geofence breach...")
            make_call()
        LAST_GEOFENCE_STATUS = geofence_status

        sleep(10)  # Check for updates every 60 seconds
