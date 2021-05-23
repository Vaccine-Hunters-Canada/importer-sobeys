import csv
from pprint import pprint

output = open('sobeys.csv', 'w')
writer = csv.DictWriter(
    output,
    fieldnames=['id', 'name', 'postal', 'province', 'city', 'address']
)

writer.writeheader()

with open('All_Sobeys_Locations.csv') as f:
    reader = csv.DictReader(f)
    for row in reader:
        address = row['sked__Address__c']
        address_parts = address.split(',')
        postal_code = address_parts.pop().strip().replace(' ', '')
        province = address_parts.pop().strip()
        city = address_parts.pop().strip()
        street_address = ' '.join(address_parts).replace('AstraZeneca', '').strip()
        writer.writerow({
            'id': row['Id'],
            'name': row['Name'].replace('AstraZeneca', '').strip(),
            'postal': postal_code,
            'province': province,
            'city': city,
            'address': street_address
        })
    