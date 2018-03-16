import json
import requests
from secrets import *

headers = {
    "X-Application-Id": traveltimeAPP_ID,
    "X-Api-Key": traveltimeAPI_KEY
}

payload = {
    "departure_searches": [
        {
          "id": "public transport from Trafalgar Square",
          "coords": {
            "lat": 51.507609,
            "lng": -0.128315
          },
          "transportation": {
            "type": "public_transport"
          },
          "departure_time": "2018-03-16T08:00:00Z",
          "travel_time": 900
        }
      ],
      "arrival_searches": [
        {
          "id": "public transport to Trafalgar Square",
          "coords": {
            "lat": 51.507609,
            "lng": -0.128315
          },
          "transportation": {
            "type": "public_transport"
          },
          "arrival_time": "2018-03-16T08:00:00Z",
          "travel_time": 900,
          "range": {
            "enabled": True,
            "width": 3600
          }
        }
      ]
}

response = requests.get(url="https://api.traveltimeapp.com")
print(response.json)
