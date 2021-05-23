import logging
import requests
from datetime import datetime

class VHC:
    BASE_URL = 'vax-availability-api-staging.azurewebsites.net'
    API_KEY = 'Bearer'
    VHC_ORG = 0

    def __init__(self, base_url, api_key, org_id):
        self.BASE_URL = base_url
        self.API_KEY = f'Bearer {api_key}'
        self.VHC_ORG = org_id

    def request_path(self, path):
        return f'https://{self.BASE_URL}/api/v1/{path}'

    def get_location(self, uuid):
        url = self.request_path(f'locations/external/{uuid}')
        response = requests.get(url, headers={'accept': 'application/json'})
        if response.status_code != 200:
            return None
        return response.json()['id']

    def create_location(self, url, external_key, name, address, postal_code, province):
        data = {
            'name': name,
            'postcode': postal_code,
            'external_key': external_key,
            'line1': address,
            'active': 1,
            'url': url,
            'organization': self.VHC_ORG,
            'province': province
        }

        headers = {'Authorization': self.API_KEY, 'Content-Type': 'application/json'}
        location_post = requests.post(self.request_path('locations/expanded'), headers=headers, json=data)
        location_id = location_post.text
        return location_id
    
    def get_availability(self, location):
        params = {
            'locationID': location,
            'min_date': str(datetime.now().date())
        }
        url = self.request_path(f'vaccine-availability/location/')
        response = requests.get(url, params=params)
        if response.status_code != 200:
            return None
        availabilities = response.json()
        if len(availabilities) > 0:
            return availabilities[0]['id']
        return None

    def create_availability(self, location, available):
        date = str(datetime.now().date())+'T00:00:00Z'
        vacc_avail_body = {
            "numberAvailable": available,
            "numberTotal": available,
            "vaccine": 1,
            "inputType": 1,
            "tags": "",
            "location": location,
            "date": date
        }
        
        vacc_avail_headers = {'accept': 'application/json', 'Authorization': self.API_KEY, 'Content-Type':'application/json'}
        response = requests.post(self.request_path('vaccine-availability'), headers=vacc_avail_headers, json=vacc_avail_body)
        return response.json()['id']

    def update_availability(self, id, location, available):
        date = str(datetime.now().date())+'T00:00:00Z'
        vacc_avail_body = {
            "numberAvailable": available,
            "numberTotal": available,
            "vaccine": 1,
            "inputType": 1,
            "tags": "",
            "location": location,
            "date": date
        }
        
        vacc_avail_headers = {'accept': 'application/json', 'Authorization': self.API_KEY, 'Content-Type':'application/json'}
        response = requests.put(self.request_path(f'vaccine-availability/{id}'), headers=vacc_avail_headers, json=vacc_avail_body)
        return response.json()['id']

    def get_or_create_location(self, url, external_key, name, address, postal_code, province):
        location = self.get_location(external_key)
        if location is None:
            logging.info(f'Create Location [{external_key}]: {name}')
            location = self.create_location(url, external_key, name, address, postal_code, province)
        else:
            logging.info(f'Found Location  [{external_key}]: {name}')
        return location

    def create_or_update_availability(self, location, available):
        availability = self.get_availability(location)
        if availability is None:
            availability = self.create_availability(location, available)
            logging.info(f'Created Availability: {available} [{availability}]')
        else:
            availability = self.update_availability(availability, location, available)
            logging.info(f'Updated Availability: {available} [{availability}]')
        return availability