from loader import bot
from telebot.types import Message
import json
from utils.API.requests import request_city
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from states.city_to_find_info import CityInfoState
import keyboards


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Введите город, в какой вы бы хотели отправиться: ')
    bot.register_next_step_handler(message, city)


def city_founding():
    with open('request_city_from_API.json', 'r', encoding='utf-8') as file:
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        result = json.load(file)
        find = re.search(pattern, result)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
    cities = list()
    for dest_id in suggestions['entities']:
        clear_destination = dest_id.get('name')
        cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
    return cities


def city_markup(city_to_find):
    request_city(city_to_find)
    cities = city_founding()
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data=f'id_{city["destination_id"]}'))
    return destinations


def city(message):
    bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=city_markup(message.text))


@bot.callback_query_handler(func=lambda call: call.data.startswith('id_'))
def city_inline_callback(call) -> None:
    for i in call.message.reply_markup.keyboard:
        for keyboard in i:
            if keyboard.callback_data == call.data:
                CityInfoState.city = keyboard.text
    call.data = re.sub('id_', '', str(call.data))
    CityInfoState.destination_id = call.data
    bot.register_next_step_handler(call.message, keyboards.inline.calendar.get_arrival_data(call.message))


@bot.message_handler()
def get_currency(message: Message) -> None:
    currency = InlineKeyboardMarkup()
    currency.add(InlineKeyboardButton(text='RUB', callback_data='RUB'))
    currency.add(InlineKeyboardButton(text='USD', callback_data='USD'))
    currency.add(InlineKeyboardButton(text='EUR', callback_data='EUR'))
    bot.send_message(message.chat.id, 'Выберите валюту рассчета', reply_markup=currency)