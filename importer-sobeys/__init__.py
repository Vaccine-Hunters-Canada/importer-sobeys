import os
import re
import csv
import logging
import requests
import datetime
from .vhc import VHC

import azure.functions as func

VACCINE_DATA = 'WyJhM3A1bzAwMDAwMDAwb3VBQUEiLCJhM3A1bzAwMDAwMDAwdjJBQUEiLCJhM3A1bzAwMDAwMDAwdjdBQUEiLCJhM3A1bzAwMDAwMDAwVzdBQUkiLCJhM3A1bzAwMDAwMDAwVzJBQUkiLCJhM3A1bzAwMDAwMDAwVzNBQUkiLCJhM3A1bzAwMDAwMDAwVzVBQUkiLCJhM3A1bzAwMDAwMDAwV1dBQVkiLCJhM3A1bzAwMDAwMDAwZjRBQUEiLCJhM3A1bzAwMDAwMDAwZk9BQVEiLCJhM3A1bzAwMDAwMDAwZllBQVEiLCJhM3A1bzAwMDAwMDAwZ2xBQUEiLCJhM3A1bzAwMDAwMDAwbnJBQUEiLCJhM3A1bzAwMDAwMDAwb3pBQUEiLCJhM3A1bzAwMDAwMDAwcVJBQVEiLCJhM3A1bzAwMDAwMDAwZkpBQVEiLCJhM3A1bzAwMDAwMDAwcDRBQUEiXQ=='

locations_file = open('sobeys.csv')
locations = csv.DictReader(locations_file)

def main(mytimer: func.TimerRequest) -> None:
    vhc = VHC(
        base_url=os.environ.get('BASE_URL'),
        api_key=os.environ.get('API_KEY'),
        org_id=os.environ.get('VHC_ORG')
    )

    for location in locations:
        today = datetime.datetime.now()
        one_week = today + datetime.timedelta(days=7)

        data = {
            'doseNumber': 1,
            'startDate': str(today.date()),
            'endDate': str(one_week.date()),
            'url': 'https://www.pharmacyappointments.ca/appointment-select',
            'vaccineData': VACCINE_DATA
        }

        availabilities = requests.post(
            f'https://api.pharmacyappointments.ca/public/locations/{location["id"]}/availability',
            json=data
        )

        availability = False
        if availabilities.status_code == 200:
            body = availabilities.json()
            for day in body['availability']:
                if day['available'] == True:
                    availability = True
        
        location_id = vhc.get_or_create_location(
            url='https://www.pharmacyappointments.ca/location-search',
            external_key=location['id'],
            name=location['name'],
            address=location['address'],
            postal_code=location['postal'],
            province=location['province']
        )

        vhc.create_or_update_availability(
            location=location_id,
            available=availability
        )

