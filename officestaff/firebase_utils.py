# firebase_utils.py

import firebase_admin
from firebase_admin import credentials, firestore

# Initialize Firebase Admin SDK
cred = credentials.Certificate('firebase_credentials/serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# Initialize Firestore client
db = firestore.client()

def fetch_meter_readings():
    """
    Fetch meter readings from Firebase Firestore.
    """
    readings_ref = db.collection('meter_readings')
    readings = readings_ref.stream()

    meter_readings = []
    for reading in readings:
        reading_data = reading.to_dict()
        meter_readings.append({
            'meter_number': reading_data['meter_number'],
            'new_reading': reading_data['new_reading'],
            'reading_date': reading_data['reading_date'],
            'meter_reader_id': reading_data.get('meter_reader_id', None)
        })

    return meter_readings
