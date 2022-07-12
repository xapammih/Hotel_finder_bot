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
                                              callback_data=f'id_{city["destination_id"]}'))
    return destinations


def city(message):

    bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=city_markup(message.text))
    bot.set_state(message.from_user.id, CityInfoState.arrival_date, message.chat.id)


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Введите город, в какой вы бы хотели отправиться: ')
    bot.register_next_step_handler(message, city)


@bot.callback_query_handler(func=lambda call: call.data.startswith('id_'))
def city_inline_callback(call) -> None:
    for i in call.message.reply_markup.keyboard:
        for keyboard in i:
            if keyboard.callback_data == call.data:
                CityInfoState.city = keyboard.text
    call.data = re.sub('id_', '', str(call.data))
    CityInfoState.destination_id = call.data
    # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    #     data['city'] = keyboard.text
    #     data['destination_id'] = call.data

    bot.register_next_step_handler(call.message, cal.get_arrival_data(call.message))


@bot.message_handler()
def get_currency(message: Message) -> None:
    currency = InlineKeyboardMarkup()
    currency.add(InlineKeyboardButton(text='RUB', callback_data='rub'))
    currency.add(InlineKeyboardButton(text='USD', callback_data='usd'))
    currency.add(InlineKeyboardButton(text='EUR', callback_data='eur'))
    bot.send_message(message.chat.id, 'Выберите валюту рассчета', reply_markup=currency)


@bot.callback_query_handler(func=lambda call: call.data in ['eur', 'rub', 'usd'])
def get_currency_callback(call) -> None:
    # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    #     data['currency'] = call.data
    CityInfoState.currency = call.data
    bot.register_next_step_handler(call.message, get_need_photo(call.message))


@bot.message_handler()
def get_need_photo(message: Message) -> None:
    bot.set_state(message.from_user.id, CityInfoState.need_photo, message.chat.id)
    is_need_photo_buttons = InlineKeyboardMarkup()
    is_need_photo_buttons.add(InlineKeyboardButton(text='Да', callback_data='нужны_фото'))
    is_need_photo_buttons.add(InlineKeyboardButton(text='Нет', callback_data='не_нужны_фото'))
    bot.send_message(message.chat.id, 'Нужны ли фото отеля?', reply_markup=is_need_photo_buttons)


@bot.callback_query_handler(func=lambda call: call.data in ['нужны_фото', 'не_нужны_фото'])
def need_photo_callback(call) -> None:
    # bot.set_state(str(call.message.chat.id), CityInfoState.count_photo)
    if call.data == 'нужны_фото':
        # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
        #     data['need_photo'] = call.data
        CityInfoState.need_photo = call.data
        bot.register_next_step_handler(call.message, get_count_photo(call.message))
    else:
        CityInfoState.need_photo = 'нет'
        bot.register_next_step_handler(call.message, ending_message(call.message))


@bot.message_handler()
def get_count_photo(message: Message) -> None:
    count_photo_buttons = InlineKeyboardMarkup()
    count_photo_buttons.add(InlineKeyboardButton(text='1', callback_data='1_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='2', callback_data='2_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='3', callback_data='3_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='4', callback_data='4_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='5', callback_data='5_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='6', callback_data='6_photo'))
    bot.send_message(message.chat.id, 'Сколько фотографий отображаем? ', reply_markup=count_photo_buttons)


@bot.callback_query_handler(func=lambda call: call.data in ['1_photo', '2_photo', '3_photo',
                                                            '4_photo', '5_photo', '6_photo'])
def count_photo_callback(call) -> None:
    # with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
    #     data['count_photo'] = call.data
    CityInfoState.count_photo = call.data
    bot.register_next_step_handler(call.message, ending_message(call.message))


def ending_message(message: Message) -> None:
    # with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
    #     data['count_photo'] = data['count_photo'][0]
    if CityInfoState.count_photo is None:
        CityInfoState.count_photo = 0
    else:
        CityInfoState.count_photo = CityInfoState.count_photo[0]
    text = f'Спасибо за предоставленную информацию, ваш запрос: \n' \
       f'Город - {CityInfoState.city}\n' \
       f'Дата заезда - {CityInfoState.arrival_date}\n' \
       f'Дата отъезда - {CityInfoState.departure_date}\n' \
       f'Валюта расчета - {CityInfoState.currency}\n' \
       f'Необходимость фотографий - {CityInfoState.need_photo}\n' \
       f'Количество фотографий - {CityInfoState.count_photo}'
    bot.send_message(message.chat.id, text)
