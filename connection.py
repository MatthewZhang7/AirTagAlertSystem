import os
from pymongo import  MongoClient
from dotenv import load_dotenv
import pandas as pd
from geopy.distance import geodesic
from pymongo.errors import ServerSelectionTimeoutError
from time import sleep
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()
MONGO_URI = os.environ["MONGODB_URI"]

# Connect to the MongoDB cluster
def connect_to_mongo():
  try:
    client = MongoClient(MONGO_URI)
    db = client['airtag_db']
    collection = db['locations']
    return collection
  except ServerSelectionTimeoutError:
     print('Error: Unable to Connect to MongoDB')
     return None
  
# Insert data into MongoDB
def process_csv(filePath):
   df = pd.read_csv(filePath)
   print("HERRO HERRO HERRO THE LOCATION IS THIS THING OKAYYYY LOOK HEREEEEEEE")
   return df[['datetime', 'name', 'locationlatitude', 'locationlongitude']]

# Insert location data into MongoDB
def insert_to_mongo(data, collection):
    if data.empty:
        print("CSV file is empty. Skipping...")
        return

    # Extract the last row of the DataFrame
    last_record = data.iloc[-1]
    print(f"Processing the most recent record: {last_record}")
    print(f"POOP PIOIOOP POOOOOOOP: {last_record['locationlongitude']}")
    location = {
        "datetime": last_record['datetime'],
        "name": last_record['name'],
        "location": {
            "type": "Point",
            "coordinates": [last_record['locationlongitude'], last_record['locationlatitude']]  # [longitude, latitude]
        }
    }
    print("eqoibqpih    pehg    ")
    print(location['location']['coordinates'][0])

    # Insert the last record into MongoDB
    collection.insert_one(location)
    print(f"Inserted the most recent record into MongoDB: {location}")


# Function to check if coordinates are within the geofence
def is_within_geofence(lat, lon, center, radius):
    distance = geodesic((lat, lon), center).meters 
    print(f"Distance from geofence center: {distance} meters")
    return distance <= radius

# Check and update if the location is within the geofence
def check_geofence_and_update(collection, geofence_center, geofence_radius):
    location = collection.find().sort("datetime", -1).limit(1)[0]
    # location = locations.sort({ id: -1 }).limit(1)
    print("Location: ")
    print(location)
    coordinates = location['location']['coordinates']
    lat, lon = coordinates[1], coordinates[0] 
    print(f"Checking geofence status for location: {lat}, {lon}")
    within_geofence = is_within_geofence(lat, lon, geofence_center, geofence_radius)
    
    # Update MongoDB with the geofence status
    collection.update_one(
        {"_id": location["_id"]},
        {"$set": {"is_within_geofence": within_geofence}}
    )

# Watchdog event handler for file changes
class CSVFileHandler(FileSystemEventHandler):
    def __init__(self, collection, geofence_center, geofence_radius):
        self.collection = collection
        self.geofence_center = geofence_center
        self.geofence_radius = geofence_radius

    def on_modified(self, event):
        if event.src_path.endswith('.csv'):
            print(f"Detected modification in file: {event.src_path}")
            location_data = process_csv(event.src_path)
            insert_to_mongo(location_data, self.collection)
            check_geofence_and_update(self.collection, self.geofence_center, self.geofence_radius)

if __name__ == "__main__":
# Geofence center (latitude, longitude)
  geofence_center = (43.4725731890728, -80.5398898404493) 
  geofence_radius = 10  # Radius in meters

  # MongoDB collection setup
  collection = connect_to_mongo()
  if collection is None:
      print("Failed to connect to MongoDB. Exiting.")
      exit(1)

  print("Connected to MongoDB.")

  # Set up watchdog observer
  path_to_watch = '/Users/matthewzhang/Desktop/Airtags copy/AirtagAlex/'
  event_handler = CSVFileHandler(collection, geofence_center, geofence_radius)
  observer = Observer()
  observer.schedule(event_handler, path=path_to_watch, recursive=False)

  # Start observer
  observer.start()
  print(f"Watching for changes in directory: {path_to_watch}")

  try:
      while True:
          sleep(1)  # Keep the script running
  except KeyboardInterrupt:
      print("Stopping file watcher...")
      observer.stop()
  observer.join()
    
