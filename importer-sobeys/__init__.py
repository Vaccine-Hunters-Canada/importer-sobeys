import os
import re
import logging
import requests
from datetime import datetime
from .vhc import VHC

import azure.functions as func

SOBEYS_BASE_URL = 'https://api.pharmacyappointments.ca/public'
VACCINE_DATA = 'WyJhM3A1bzAwMDAwMDAwb3VBQUEiLCJhM3A1bzAwMDAwMDAwdjJBQUEiLCJhM3A1bzAwMDAwMDAwdjdBQUEiLCJhM3A1bzAwMDAwMDAwVzdBQUkiLCJhM3A1bzAwMDAwMDAwVzJBQUkiLCJhM3A1bzAwMDAwMDAwVzNBQUkiLCJhM3A1bzAwMDAwMDAwVzVBQUkiLCJhM3A1bzAwMDAwMDAwV1dBQVkiLCJhM3A1bzAwMDAwMDAwZjRBQUEiLCJhM3A1bzAwMDAwMDAwZk9BQVEiLCJhM3A1bzAwMDAwMDAwZllBQVEiLCJhM3A1bzAwMDAwMDAwZ2xBQUEiLCJhM3A1bzAwMDAwMDAwbnJBQUEiLCJhM3A1bzAwMDAwMDAwb3pBQUEiLCJhM3A1bzAwMDAwMDAwcVJBQVEiLCJhM3A1bzAwMDAwMDAwZkpBQVEiLCJhM3A1bzAwMDAwMDAwcDRBQUEiXQ=='

locations = {
    'Ontario': {
        'Ottawa': {'lat': 45.4215296, 'lng': -75.69719309999999},
        'Toronto': {'lat': 43.653226, 'lng': -79.3831843},
    },
    'Alberta': {
        'Calgary': {'lat': 51.04473309999999, 'lng': -114.0718831},
        'Edmonton': {'lat': 53.5461245, 'lng': -113.4938229},
    },
    'British Columbia': {
        'Vancouver': {'lat': 49.2827291, 'lng': -123.1207375},
        'Victoria': {'lat': 48.4284207, 'lng': -123.3656444}
    }
}

def main(mytimer: func.TimerRequest) -> None:
    vhc = VHC(
        base_url=os.environ.get('BASE_URL'),
        api_key=os.environ.get('API_KEY'),
        org_id=os.environ.get('VHC_ORG')
    )

    for province in locations:
        for city in locations[province]:
            location_data = locations[province][city]
            data = {
                'doseNumber': 1,
                'fromDate': str(datetime.now().date()),
                'location': location_data,
                'locationQuery': {'includePools': ['default']},
                'url': 'https://www.pharmacyappointments.ca/location-select',
                'vaccineData': VACCINE_DATA
            }
            response = requests.post(
                f'{SOBEYS_BASE_URL}/locations/search', 
                headers={'content-type': 'application/json'},
                json=data
            )
            logging.info(f'City: {city}, {province}')
            if response.status_code == 200:
                availabilities = response.json()['locations']
                if len(availabilities) > 0:
                    for sobey in availabilities:
                        postal = re.findall(r'[A-Z]{1}[0-9]{1}[A-Z]{1}\s*[0-9]{1}[A-Z]{1}[0-9]{1}', sobey['displayAddress'])[0]

                        location_id = vhc.get_or_create_location(
                            url='https://www.pharmacyappointments.ca/location-search',
                            external_key=sobey['extId'],
                            name=sobey['name'],
                            address=sobey['displayAddress'],
                            postal_code=postal.replace(' ', ''),
                            province=province
                        )

                        vhc.create_or_update_availability(
                            location=location_id,
                            available=1
                        )

