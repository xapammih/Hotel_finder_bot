from datetime import date

from keyboards.inline import calendar
import keyboards.inline.calendar as cal
from loader import bot
from states.city_to_find_info import CityInfoState
from telebot.types import Message
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import utils.API
import re
from telegram_bot_calendar import DetailedTelegramCalendar, LSTEP


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
    bot.send_message(message.chat.id, 'Выберите валюту рассчета')

    bot.set_state(message.from_user.id, CityInfoState.need_photo, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['currency'] = message.text


@bot.message_handler(state=CityInfoState.need_photo)
def get_need_photo(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Нужны ли фото отеля?')

    bot.set_state(message.from_user.id, CityInfoState.count_photo, message.chat.id)

    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['need_photo'] = message.text


@bot.message_handler(state=CityInfoState.count_photo)
def get_count_photo(message: Message) -> None:
    bot.send_message(message.from_user.id, 'Сколько фотографий отображаем? ')
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['count_photo'] = message.text

    text = f'Спасибо за предоставленную информацию, ваш запрос: \n' \
           f'Город - {data["city"]}\n' \
           f'Дата заезда - {data["arrival_data"]}\n' \
           f'Дата отъезда - {data["departure_data"]}\n' \
           f'Валюта расчета - {data["currency"]}\n' \
           f'Необходимость фотографий - {data["need_photo"]}\n' \
           f'Количество фотографий - {data["count_photo"]}'
    bot.send_message(message.from_user.id, text)
    bot.delete_state(message.from_user.id)