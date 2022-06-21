from datetime import date

import keyboards.inline.calendar as cal
from loader import bot
from states.city_to_find_info import CityInfoState
from telebot.types import Message
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import utils.API
import re


def city_founding():
    with open('request_from_API.json', 'r', encoding='utf-8') as file:
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
    utils.API.requests.main_request(city_to_find)
    cities = city_founding()
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data=f'{city["destination_id"]}'))
    return destinations


def city(message):
    bot.set_state(message.from_user.id, CityInfoState.city, message.chat.id)
    bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=city_markup(message.text))
    bot.set_state(message.from_user.id, CityInfoState.arrival_date, message.chat.id)


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Введите город, в какой вы бы хотели отправиться: ')
    bot.register_next_step_handler(message, city)


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def city_inline_callback(call) -> None:
    print(call.data)
    for i in call.message.reply_markup.keyboard:
        for keyboard in i:
            if keyboard.callback_data == call.data:
                print(keyboard.text)
                print(call.data)
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['city'] = keyboard.text
        data['destination_id'] = call.data

    bot.set_state(str(call.message.chat.id), CityInfoState.arrival_date)
    bot.register_next_step_handler(call.message, cal.get_arrival_data(call.message))


@bot.message_handler(state=CityInfoState.currency)
def get_currency(message: Message) -> None:
    currency = InlineKeyboardMarkup()
    currency.add(InlineKeyboardButton(text='RUB', callback_data='rub'))
    currency.add(InlineKeyboardButton(text='USD', callback_data='usd'))
    currency.add(InlineKeyboardButton(text='EUR', callback_data='eur'))
    bot.send_message(message.chat.id, 'Выберите валюту рассчета', reply_markup=currency)
    bot.register_next_step_handler(message, get_currency_callback)


@bot.callback_query_handler(func=lambda call: call.data in ['eur', 'rub', 'usd'])
def get_currency_callback(call) -> None:
    with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        data['currency'] = call.data
    bot.register_next_step_handler(call.message, get_need_photo(call.message))


@bot.message_handler(state=CityInfoState.need_photo)
def get_need_photo(message: Message) -> None:
    bot.set_state(message.from_user.id, CityInfoState.need_photo, message.chat.id)
    is_need_photo_buttons = InlineKeyboardMarkup()
    is_need_photo_buttons.add(InlineKeyboardButton(text='Да', callback_data='нужны_фото'))
    is_need_photo_buttons.add(InlineKeyboardButton(text='Нет', callback_data='не_нужны_фото'))
    bot.send_message(message.chat.id, 'Нужны ли фото отеля?', reply_markup=is_need_photo_buttons)
    bot.set_state(message.chat.id, CityInfoState.count_photo)


@bot.callback_query_handler(func=lambda call: call.data in ['нужны_фото', 'не_нужны_фото'])
def need_photo_callback(call) -> None:
    if call.message == 'нужны_фото':
        with bot.retrieve_data(call.chat.id, call.message.chat.id) as data:
            data['need_photo'] = call.data
        bot.register_next_step_handler(call.message, get_count_photo(call.message))
    else:
        bot.register_next_step_handler(call.message, ending_message(call.message))


@bot.message_handler(state=CityInfoState.count_photo)
def get_count_photo(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Сколько фотографий отображаем? ')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = message.text
    bot.register_next_step_handler(message.chat.id, ending_message(message))


@bot.message_handler(state=CityInfoState.count_photo)
def ending_message(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        print(data)
        text = f'Спасибо за предоставленную информацию, ваш запрос: \n' \
           f'Город - {data["city"]}\n' \
           f'Дата заезда - {data["arrival_data"]}\n' \
           f'Дата отъезда - {data["departure_data"]}\n' \
           f'Валюта расчета - {data["currency"]}\n' \
           f'Необходимость фотографий - {data["need_photo"]}\n' \
           f'Количество фотографий - {data["count_photo"]}'
    bot.send_message(message.from_user.id, text)
    bot.delete_state(message.from_user.id)
