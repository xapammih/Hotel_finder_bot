import telebot
import config
import requests
import json

bot = telebot.TeleBot(config.token)


def main_request():
    url = 'https://hotels4.p.rapidapi.com/locations/v2/search'
    querystring = {"query": "new york", "locale": "en_US", "currency": "USD"}
    headers = {
        'x-rapidapi-host': "hotels4.p.rapidapi.com",
        'x-rapidapi-key': "e800e098c4msh474c79e3bce3792p154ddajsn238a4e9968f5"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    with open('test.json', 'w') as file:
        json.dump(response.text, file, indent=4)


def low_high_buttons(message):
    max_hotels_to_find = 20
    town_to_find = input(bot.send_message(message.from_user.id, "Введите город для поиска отелей: "))
    number_hotels_to_find = int(input(bot.send_message(message.from_user.id, "Введите кол-во отелей для поиска: ")))
    if number_hotels_to_find > max_hotels_to_find:
        bot.send_message(message.from_user.id, f'Кол-во отелей не может быть больше {max_hotels_to_find}')
        number_hotels_to_find = 0
    need_photos = input(bot.send_message(message.from_user.id, "Нужны ли фотографии отелей?Да/Нет ")).lower()
    if need_photos == 'да':
        town_to_find = input(bot.send_message(message.from_user.id, "Сколько фотографий необходимо вывести? "))


@bot.message_handler(commands=['start', 'lowprice', 'highprice', 'bestdeal', 'history'])
def get_text_messages(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/lowprice":
        low_high_buttons(message)
    elif message.text == "/highprice":
        low_high_buttons(message)
    elif message.text == "/bestdeal":
        town_to_find = input(bot.send_message(message.from_user.id, "Введите город для поиска отелей: "))
        price_range = input(bot.send_message(message.from_user.id, "Введите диапазон цен: ")).split('-')
        distance_range = input(bot.send_message(message.from_user.id, "Введите диапазон расстояния от центра: ")).split('-')
        number_hotels_to_find = 0
        max_hotels_to_find = 20
        while number_hotels_to_find == 0 or number_hotels_to_find > max_hotels_to_find:
            number_hotels_to_find = int(input(bot.send_message(message.from_user.id, "Введите кол-во отелей для поиска: ")))
            bot.send_message(message.from_user.id, f'Кол-во отелей не может быть больше {max_hotels_to_find}')
    elif message.text == '/history':
        bot.send_message(message.from_user.id, 'История')

    elif message.text == "/stop":
        ending_text_messages(message)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

@bot.message_handler(commands=['stop'])
def ending_text_messages(message):
    bot.send_message(message.from_user.id, 'Увидимся! Всего хорошего')
    exit()


if __name__ == "__main__":
    # main_request()
    try:
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    except Exception as r:
        print("Непридвиденная ошибка: ", r)
    finally:
        print("Здесь всё закончилось")