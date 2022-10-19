from loader import bot
from telebot.types import Message
import json
from utils.API.requests import request_city, request_hotels,request_hotels_photo, request_rub_currency
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from states.city_to_find_info import CityInfoState
from keyboards.inline import dialog_keyboards, calendar
from config_data import config
from telebot import types
import loguru
import requests


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
    print(message.chat.id)
    CityInfoState.data[message.chat.id] = {'city': None, 'destination_id': None, 'arrival_date': None, 'departure_date': None,
                        'days_in_hotel': None, 'criterion': None, 'currency': None, 'need_photo': None,
                        'count_photo': None, 'hotels_count': None, 'distance_from_center': None,
                        'max_cost': None, 'min_cost': None}
    bot.send_message(message.from_user.id, f'Введите город, в какой вы бы хотели отправиться: ')
    bot.register_next_step_handler(message, city)


def city_founding() -> list:
    with open('request_city_from_API.json', 'r', encoding='utf-8') as file:
        pattern = r'(?<="CITY_GROUP",).+?[\]]'
        result = json.load(file)
        find = re.search(pattern, result)
    if find:
        suggestions = json.loads(f"{{{find[0]}}}")
    cities = list()
    for dest_id in suggestions['entities']:
        clear_destination = re.sub(r'<.*?>', '', dest_id['caption'])
        cities.append({'city_name': clear_destination, 'destination_id': dest_id['destinationId']})
    return cities


def city_markup(city_to_find: str):
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
                CityInfoState.data[call.message.chat.id]['city'] = keyboard.text
    call.data = call.data[3:]
    CityInfoState.destination_id = call.data
    bot.send_message(call.message.chat.id, 'Записал! Введите дату заезда: ')
    calendar.get_arrival_data(call.message)
    bot.set_state(user_id=call.from_user.id, state=CityInfoState.arrival_date, chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data in ['EUR', 'RUB', 'USD'])
def get_currency(call) -> None:
    CityInfoState.data[call.message.chat.id]['currency'] = call.data
    bot.send_message(call.message.chat.id, 'По каким критериям выбираем отель? ',
                     reply_markup=dialog_keyboards.get_criterion_keyboard())
    bot.set_state(user_id=call.from_user.id, state=CityInfoState.criterion, chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data in ['low_price', 'high_price', 'best_deal'])
def criterion_callback(call) -> None:
    CityInfoState.data[call.message.chat.id]['criterion'] = call.data
    bot.set_state(user_id=call.from_user.id, state=CityInfoState.need_photo, chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Нужны ли фото отеля?', reply_markup=dialog_keyboards.need_photos_keyboard())


@bot.callback_query_handler(func=lambda call: call.data in ['нужны_фото', 'не_нужны_фото'])
def need_photo_callback(call) -> None:
    if call.data == 'нужны_фото':
        CityInfoState.data[call.message.chat.id]['need_photo'] = call.data
        bot.set_state(user_id=call.from_user.id, state=CityInfoState.count_photo, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Сколько фотографий отображаем? ',
                         reply_markup=dialog_keyboards.count_photo_keyboard())
    else:
        CityInfoState.data[call.message.chat.id]['need_photo'] = 'нет'
        CityInfoState.data[call.message.chat.id]['count_photo'] = 0
        if CityInfoState.data[call.message.chat.id]['criterion'] == 'best_deal':
            bot.set_state(user_id=call.from_user.id, state=CityInfoState.max_cost, chat_id=call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Введите максимальную цену за сутки: ')
        else:
            ending_message(call.message)


@bot.callback_query_handler(func=lambda call: call.data in ['1_photo', '2_photo', '3_photo',
                                                            '4_photo', '5_photo', '6_photo'])
def count_photo_callback(call) -> None:
    CityInfoState.data[call.message.chat.id]['count_photo'] = call.data[0]
    if CityInfoState.data[call.message.chat.id]['criterion'] == 'best_deal':
        bot.set_state(user_id=call.from_user.id, state=CityInfoState.max_cost, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Введите максимальную цену за сутки: ')
    else:
        ending_message(call.message)


@bot.message_handler(state=CityInfoState.max_cost)
def bestdeal_price_info(message: Message):
    if CityInfoState.currency == 'RUB':
        CityInfoState.data[message.from_user.id]['max_cost'] = int(message.text)
    else:
        CityInfoState.data[message.from_user.id]['max_cost'] = message.text
    bot.set_state(user_id=message.from_user.id, state=CityInfoState.distance_from_center, chat_id=message.chat.id)
    bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра: ')


@bot.message_handler(state=CityInfoState.distance_from_center)
def bestdeal_distance_info(message: Message):
    CityInfoState.data[message.from_user.id]['distance_from_center'] = message.text
    ending_message(message)


def ending_message(message: Message) -> None:
    text = (
       f'Спасибо за предоставленную информацию, ваш запрос: \n'
       f'Город - {CityInfoState.data[message.chat.id]["city"]}\n'
       f'Дата заезда - {CityInfoState.data[message.chat.id]["arrival_date"]}\n'
       f'Дата отъезда - {CityInfoState.data[message.chat.id]["departure_date"]}\n'
       f'Критерий выбора отеля - {CityInfoState.data[message.chat.id]["criterion"]}\n'
       f'Валюта расчета - {CityInfoState.data[message.chat.id]["currency"]}\n'
       f'Необходимость фотографий - {CityInfoState.data[message.chat.id]["need_photo"]}\n'
       f'Количество фотографий - {CityInfoState.data[message.chat.id]["count_photo"]}\n'
       f'Количество дней в отеле - {CityInfoState.data[message.chat.id]["days_in_hotel"]}'
    )
    bot.send_message(message.chat.id, text)
    show_hotels(message)


def show_hotels(message: Message) -> None:
    request_hotels(message)
    if CityInfoState.data[message.chat.id]['criterion'] == 'low_price':
        hotels_to_show = sorted(search_lowprice_highprice(), key=lambda x: x['price'])
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        else:
            bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
            for i in range(config.max_hotels_count):
                if int(CityInfoState.data[message.chat.id]['count_photo']) != 0:
                    bot.send_media_group(message.chat.id, search_photos(message, hotels_to_show[i]))
                bot.send_message(message.chat.id, sending_hotels_message(hotels_to_show, i, message))
            bot.delete_state(message.from_user.id, message.chat.id)
    elif CityInfoState.data[message.chat.id]['criterion'] == 'high_price':
        hotels_to_show = sorted(search_lowprice_highprice(), key=lambda x: x['price'], reverse=True)
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        else:
            bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
            for i in range(config.max_hotels_count):
                if int(CityInfoState.data[message.chat.id]['count_photo']) != 0:
                    bot.send_media_group(message.chat.id, search_photos(message, hotels_to_show[i]))
                bot.send_message(message.chat.id, sending_hotels_message(hotels_to_show, i, message))
            bot.delete_state(message.from_user.id, message.chat.id)
    elif CityInfoState.data[message.chat.id]['criterion'] == 'best_deal':
        hotels_to_show = sorted(search_bestdeal(message), key=lambda x: x['distance'])
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено, уточните критерий поиска! ')
            bot.set_state(user_id=message.from_user.id, state=CityInfoState.max_cost, chat_id=message.chat.id)
            bot.send_message(message.chat.id, 'Введите максимальную цену за сутки: ')
        else:
            bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
            for i in range(len(hotels_to_show)):
                if int(CityInfoState.data[message.chat.id]['count_photo']) != 0:
                    bot.send_media_group(message.chat.id, search_photos(message, hotels_to_show[i]))
                bot.send_message(message.chat.id, sending_hotels_message(hotels_to_show, i, message))
            bot.delete_state(message.from_user.id, message.chat.id)


def sending_hotels_message(hotels: list, index: int, message) -> str:
    full_price = round((hotels[index]['price']) * CityInfoState.data[message.chat.id]['days_in_hotel'])
    if CityInfoState.data[message.chat.id]['currency'] == 'RUB':
        full_price *= round(request_rub_currency())
        dayly_price = round(hotels[index]['price'] * request_rub_currency())
    else:
        dayly_price = hotels[index]['price']
    text = f"🏨Наименование: {hotels[index]['name']}\n" \
           f"⭐Рейтинг: {hotels[index]['starrating']}\n" \
           f"🌎Адрес: {hotels[index]['address']}\n" \
           f"💴Цена за сутки: {dayly_price} {CityInfoState.data[message.chat.id]['currency']}\n" \
           f"💰Цена за {CityInfoState.data[message.chat.id]['days_in_hotel']} суток: " \
           f"{full_price} {CityInfoState.data[message.chat.id]['currency']}\n" \
           f"➡️Расстояние до центра: {hotels[index]['distance']}"
    return text


def search_lowprice_highprice() -> list:
    hotels_list = []
    with open('request_hotels_from_API.json', 'r', encoding='utf-8') as file:
        pattern = r'(?<=,)"results":.+?(?=,"pagination)'
        result = json.load(file)
        price_find = re.search(pattern, result)
        if price_find:
            request_hotels = json.loads(f"{{{price_find[0]}}}")
            try:
                for i in request_hotels['results']:
                    hotels_list.append({'id': i['id'], 'name': i['name'], 'starrating': i['starRating'],
                                        'address': i.get('address', []).get('streetAddress'),
                                        'distance': i.get('landmarks', [])[0].get('distance', ''),
                                        'price': i.get('ratePlan', []).get('price', []).get('exactCurrent', 0)})
                print(hotels_list)
                return hotels_list

            except AttributeError:
                hotels_list.append(dict())
                return hotels_list


def search_bestdeal(message: Message):
    hotels_list_bestdeal = []
    with open('request_hotels_from_API.json', 'r', encoding='utf-8') as file:
        pattern = r'(?<=,)"results":.+?(?=,"pagination)'
        result = json.load(file)
        price_find = re.search(pattern, result)
        if price_find:
            request_hotels = json.loads(f"{{{price_find[0]}}}")
            try:
                for i in request_hotels['results']:
                    if CityInfoState.data[message.chat.id]['currency'] == 'RUB':
                        current_cost = round(float(i.get('ratePlan', []).get('price', []).get('exactCurrent', 0))
                                             * float(request_rub_currency()))
                        current_dist = i.get('landmarks', [])[0].get('distance', '').split(' ')[0]
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
    hotels_photo_lst = []
    pattern = '{size}'
    result = json.loads(request_hotels_photo(cur_hotel.get('id')))
    for elem in result['hotelImages']:
        temp = re.sub(pattern, 'y', elem['baseUrl'])
        if temp == '':
            temp = open("utils/misc/No_image_available.svg.png", 'rb')
        if len(hotels_photo_lst) < int(CityInfoState.data[message.chat.id]['count_photo']):
            if str(requests.get(temp)).startswith('<Response [2'):
                hotels_photo_lst.append(types.InputMediaPhoto(temp))
        else:
            break
    return hotels_photo_lst



