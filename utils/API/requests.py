import json
import requests
from config_data import config
from states.city_to_find_info import CityInfoState


def request_city(city_to_find):
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {"query": city_to_find, "locale": "en_UK", "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config.RAPID_API_KEY
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            with open('request_city_from_API.json', 'w') as file:
                json.dump(response.text, file, sort_keys=True, indent=4)
    except Exception as err:
        print(f'Ошибка {err}')


def request_hotels():
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": CityInfoState.destination_id, "pageNumber": "1",
                   "pageSize": "25", "checkIn": CityInfoState.arrival_date,
                   "checkOut": CityInfoState.departure_date, "adults1": "1", "sortOrder": "PRICE",
                   "locale": "en_US", "currency": CityInfoState.currency}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config.RAPID_API_KEY
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            with open('request_hotels_from_API.json', 'w') as file:
                json.dump(response.text, file, sort_keys=True, indent=4)
                json.load(file)
    except Exception as err:
        print(f'Ошибка {err}')
