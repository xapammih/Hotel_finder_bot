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


@bot.message_handler(commands=['start', 'lowprice', 'highprice', 'bestdeal', 'history', 'help'])
def get_text_messages(message):
    s = message.text
    s = s.lower()
    if s == "/start":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
        bot.send_message(message.from_user.id, f'{type(message.text)}')

    elif s == "/lowprice":
        low_high_buttons(message)
    elif message.text == "/highprice":
        low_high_buttons(message)
    elif message.text == "/bestdeal":
        pass
    elif message.text.lower == '/history':
        bot.send_message(message.from_user.id, 'История')

    elif message.text.lower == "/stop":
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
