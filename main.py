from config_data import config
from loader import bot
import requests
import json
from handlers.default_handlers import start

def main_request():
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {"query": "london", "locale": "en_UK", "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': config.rapidapi_key
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    with open('test.json', 'w') as file:
        json.dump(response.text, file, sort_keys=True, indent=4)


if __name__ == "__main__":
    main_request()
    try:
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    except Exception as r:
        print("Непридвиденная ошибка: ", r)
    finally:
        print("Здесь всё закончилось")
