import json
import requests
from config_data import config
from states.city_to_find_info import CityInfoState
from telebot.types import Message


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


def request_hotels(message: Message):
    url = "https://hotels4.p.rapidapi.com/properties/list"
    querystring = {"destinationId": CityInfoState.data[message.chat.id]["destination_id"], "pageNumber": "1",
                   "pageSize": "25", "checkIn": CityInfoState.data[message.chat.id]["arrival_date"],
                   "checkOut": CityInfoState.data[message.chat.id]["departure_date"], "adults1": "1", "sortOrder": "PRICE",
                   "locale": "en_US", "currency": CityInfoState.data[message.chat.id]["currency"]}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config.RAPID_API_KEY
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring, timeout=10)
        if response.status_code == requests.codes.ok:
            with open('request_hotels_from_API.json', 'w') as file:
                json.dump(response.text, file, sort_keys=True, indent=4)
    except Exception as err:
        print(f'Ошибка {err}')


def request_hotels_photo(hotel_id):
    url = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"
    querystring = {"id": hotel_id}

    headers = {
        "X-RapidAPI-Key": "e800e098c4msh474c79e3bce3792p154ddajsn238a4e9968f5",
        "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
    }
    try:
        response = requests.request("GET", url, headers=headers, params=querystring)
        if response.status_code == requests.codes.ok:
            return response.text
    except Exception as err:
        print(f'Ошибка {err}')