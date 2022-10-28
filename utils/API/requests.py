import json
import re
import requests
from config_data import config
from states.city_to_find_info import CityInfoState
from telebot.types import Message, InputMediaPhoto


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
            return response.text
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
            return response.text
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


def request_rub_currency():
    url = 'https://www.cbr-xml-daily.ru/daily_json.js'
    try:
        response = requests.request("GET", url)
        if response.status_code == requests.codes.ok:
            return response.json()['Valute']['USD']['Value']
    except Exception:
        return response.json()['Valute']['USD']['Previous']


def city_founding(cur_city) -> list:
    """
    Функция формирует список с вариантами выбора города из API
    :return:
    """
    pattern = r'(?<="CITY_GROUP",).+?[\]]'
    result = request_city(cur_city)
    find = re.search(pattern, result)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
    cities = list()
    for dest_id in suggestions['entities']:
        clear_destination = re.sub(r'<.*?>', '', dest_id['caption'])
        cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
    return cities


def search_lowprice_highprice(message: Message) -> list:
    """
    Функция формирует список отелей для ценового критерия lowprice и highprice
    :return:
    """
    hotels_list = []
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    result = request_hotels(message)
    price_find = re.search(pattern, result)
    if price_find:
        hotels = json.loads(f"{{{price_find[0]}}}")
        try:
            for i in hotels['results']:
                hotels_list.append({'id': i['id'], 'name': i['name'], 'starrating': i['starRating'],
                                    'address': i.get('address', []).get('streetAddress'),
                                    'distance': i.get('landmarks', [])[0].get('distance', ''),
                                    'price': i.get('ratePlan', []).get('price', []).get('exactCurrent', 0),
                                    'hotel_link': f'https://hotels.com/ho{i["id"]}'},
                                   )
            return hotels_list

        except AttributeError:
            hotels_list.append(dict())
            return hotels_list


def search_bestdeal(message: Message):
    """
    Функция формирует список отелей для ценового критерия bestdeal
    :param message:
    :return:
    """
    hotels_list_bestdeal = []
    pattern = r'(?<=,)"results":.+?(?=,"pagination)'
    result = request_hotels(message)
    price_find = re.search(pattern, result)
    if price_find:
        hotels = json.loads(f"{{{price_find[0]}}}")
        try:
            for i in hotels['results']:
                current_dist = i.get('landmarks', [])[0].get('distance', '').split(' ')[0]
                if CityInfoState.data[message.chat.id]['currency'] == 'RUB':
                    current_cost = round(float(i.get('ratePlan', []).get('price', []).get('exactCurrent', 0))
                                         * float(request_rub_currency()))
                else:
                    current_cost = round(float(i.get('ratePlan', []).get('price', []).get('exactCurrent', 0)))
                if float(current_cost) < float(CityInfoState.data[message.chat.id]['max_cost']) and \
                    float(CityInfoState.data[message.chat.id]['distance_from_center']) > float(current_dist):
                    hotels_list_bestdeal.append({'id': i['id'], 'name': i['name'], 'starrating': i['starRating'],
                                        'address': i.get('address', []).get('streetAddress'),
                                        'distance': i.get('landmarks', [])[0].get('distance', ''),
                                        'price': i.get('ratePlan', []).get('price', []).get('exactCurrent', 0)})

            return hotels_list_bestdeal
        except AttributeError:
            hotels_list_bestdeal.append(dict())
            return hotels_list_bestdeal


def search_photos(message: Message, cur_hotel: dict):
    """
    Функция, формирующая список медиаданных(фотографий) для одного отеля
    :param message:
    :param cur_hotel:
    :return:
    """
    hotels_photo_lst = []
    pattern = '{size}'
    result = json.loads(request_hotels_photo(cur_hotel.get('id')))
    for elem in result['hotelImages']:
        temp = re.sub(pattern, 'y', elem['baseUrl'])
        if temp == '':
            temp = open("utils/misc/No_image_available.svg.png", 'rb')
        if len(hotels_photo_lst) < int(CityInfoState.data[message.chat.id]['count_photo']):
            if str(requests.get(temp)).startswith('<Response [2'):
                hotels_photo_lst.append(InputMediaPhoto(temp))
        else:
            break
    return hotels_photo_lst

