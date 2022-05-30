import json
import requests
from config_data import config


def main_request(city_to_find):
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {"query": city_to_find, "locale": "en_UK", "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config.RAPID_API_KEY
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    with open('request_from_API.json', 'w') as file:
        json.dump(response.text, file, sort_keys=True, indent=4)