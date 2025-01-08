# AirTag Geofence Alert System

This project is a Python-based system that tracks AirTag coordinates, checks if the AirTag breaches a defined geofence, and triggers a phone call using Twilio to notify the user. The system is built using MongoDB for storing location data and integrates file monitoring to update geofence statuses in real-time.

## Features

- **Geofence Monitoring**: Define a geofence by specifying a central point and radius. The script checks if the AirTag remains within the geofence.
- **Real-time Updates**: Monitors changes in CSV files for new location data and updates the database accordingly.
- **Twilio Integration**: Automatically triggers a phone call when the AirTag breaches the geofence.
- **Modular Design**: Two separate scripts handle geofence monitoring and notifications.

## Requirements

- Python 3.8 or later
- MongoDB instance
- Twilio account for phone call notifications
- Environment variables for sensitive credentials
- CSV files containing AirTag location data

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/airtag-geofence-alert.git
   cd airtag-geofence-alert
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   Create a `.env` file in the project root and configure the following:

   ```env
   MONGODB_URI=your_mongodb_connection_string
   ACCOUNT_SID=your_twilio_account_sid
   AUTH_TOKEN=your_twilio_auth_token
   TO_PHONE_NUMBER=your_phone_number
   FROM_PHONE_NUMBER=your_twilio_phone_number
   ```

4. **Prepare the MongoDB database**:
   Ensure your MongoDB instance is running and create a database named `airtag_db` with a collection named `locations`.

5. **Place the CSV file**:
   Save AirTag location data as CSV files in the directory you want to monitor.

## Usage

### 1. Geofence Monitoring

Run the `connection.py` script to start monitoring AirTag coordinates and update the geofence status:

```bash
python connection.py
```

- **Parameters**:

  - Geofence center: Hardcoded as `(43.4725731890728, -80.5398898404493)`
  - Geofence radius: Hardcoded as `10` meters (adjust in `connection.py` as needed)
  - CSV Directory: Hardcoded in `path_to_watch` (update this in `connection.py`).

- **Functionality**:
  - Monitors the specified directory for CSV file changes.
  - Extracts the most recent location data and stores it in MongoDB.
  - Checks if the AirTag is within the geofence and updates the database.

### 2. Notification System

Run the `notifications.py` script to receive phone call alerts when the geofence is breached:

```bash
python notifications.py
```

- **Functionality**:
  - Checks the geofence status of the latest record in MongoDB.
  - Initiates a Twilio call if the AirTag moves outside the geofence.

## CSV File Format

The CSV files must include the following columns:

- `datetime`: Timestamp of the location record
- `name`: Name of the AirTag
- `locationlatitude`: Latitude of the AirTag
- `locationlongitude`: Longitude of the AirTag

## Dependencies

- [pymongo](https://pymongo.readthedocs.io/)
- [watchdog](https://python-watchdog.readthedocs.io/)
- [twilio](https://www.twilio.com/docs/libraries/python)
- [geopy](https://geopy.readthedocs.io/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [pandas](https://pandas.pydata.org/)

Install all dependencies with:

```bash
pip install -r requirements.txt
```

## Limitations

- The geofence center and radius are hardcoded in `connection.py`. Consider adding CLI arguments or a configuration file for flexibility.
- MongoDB and Twilio credentials must be securely managed using environment variables.
- This script currently supports only one AirTag at a time.

## Future Improvements

- Add support for multiple AirTags and geofences.
- Implement a web dashboard for visualization.
- Enhance error handling and logging.
- Make the geofence parameters configurable via a user interface.
