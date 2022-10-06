from loader import bot
from telebot.types import Message
import json
from utils.API.requests import request_city, request_hotels
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from states.city_to_find_info import CityInfoState
import keyboards
from config_data import config


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
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
    call.data = re.sub('id_', '', str(call.data))
    CityInfoState.destination_id = call.data
    bot.register_next_step_handler(call.message, keyboards.inline.calendar.get_arrival_data(call.message))


@bot.callback_query_handler(func=lambda call: call.data in ['EUR', 'RUB', 'USD'])
def get_currency(call) -> None:
    CityInfoState.data[call.message.chat.id]['currency'] = call.data
    bot.register_next_step_handler(call.message, get_criterion(call.message))


@bot.message_handler()
def get_criterion(message: Message) -> None:
    criterion_buttons = InlineKeyboardMarkup()
    criterion_buttons.add(InlineKeyboardButton(text='Минимальная цена', callback_data='low_price'))
    criterion_buttons.add(InlineKeyboardButton(text='Максимальная цена', callback_data='high_price'))
    criterion_buttons.add(InlineKeyboardButton(text='Лучшее предложение!', callback_data='best_deal'))
    bot.send_message(message.chat.id, 'По каким критериям выбираем отель? ', reply_markup=criterion_buttons)


@bot.callback_query_handler(func=lambda call: call.data in ['low_price', 'high_price', 'best_deal'])
def criterion_callback(call) -> None:
    CityInfoState.data[call.message.chat.id]['criterion'] = call.data
    bot.register_next_step_handler(call.message, get_need_photo(call.message))


@bot.message_handler()
def get_need_photo(message: Message) -> None:
    is_need_photo_buttons = InlineKeyboardMarkup()
    is_need_photo_buttons.add(InlineKeyboardButton(text='Да', callback_data='нужны_фото'))
    is_need_photo_buttons.add(InlineKeyboardButton(text='Нет', callback_data='не_нужны_фото'))
    bot.send_message(message.chat.id, 'Нужны ли фото отеля?', reply_markup=is_need_photo_buttons)


@bot.callback_query_handler(func=lambda call: call.data in ['нужны_фото', 'не_нужны_фото'])
def need_photo_callback(call) -> None:
    if call.data == 'нужны_фото':
        CityInfoState.data[call.message.chat.id]['need_photo'] = call.data
        bot.register_next_step_handler(call.message, get_count_photo(call.message))
    else:
        CityInfoState.data[call.message.chat.id]['need_photo'] = 'нет'
        CityInfoState.data[call.message.chat.id]['count_photo'] = 0
        if CityInfoState.data[call.message.chat.id]['criterion'] == 'best_deal':
            bot.send_message(call.message.chat.id, 'Введите максимальную цену за сутки: ')
            bot.register_next_step_handler(call.message, bestdeal_price_info(call.message))
        else:
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
    CityInfoState.data[call.message.chat.id]['count_photo'] = call.data[0]
    if CityInfoState.data[call.message.chat.id]['criterion'] == 'best_deal':
        bot.register_next_step_handler(call.message, bestdeal_price_info(call.message))
    else:
        bot.register_next_step_handler(call.message, ending_message(call.message))


@bot.message_handler()
def bestdeal_price_info(message: Message):
    # if message.text.isdigit():
    CityInfoState.data[message.chat.id]['max_cost'] = message.text
    # else:
    #     bot.send_message(message.chat.id, 'Неверный ввод, повторите: ')
    #     return
    bot.register_next_step_handler(message.from_user.id, bestdeal_distance_info(message))


@bot.message_handler()
def bestdeal_distance_info(message: Message):
    bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра: ')
    CityInfoState.data[message.chat.id]['distance_from_center'] = message.text
    bot.register_next_step_handler(message, ending_message(message))


def ending_message(message: Message) -> None:
    text = f'Спасибо за предоставленную информацию, ваш запрос: \n' \
       f'Город - {CityInfoState.data[message.chat.id]["city"]}\n' \
       f'Дата заезда - {CityInfoState.data[message.chat.id]["arrival_date"]}\n' \
       f'Дата отъезда - {CityInfoState.data[message.chat.id]["departure_date"]}\n' \
       f'Критерий выбора отеля - {CityInfoState.data[message.chat.id]["criterion"]}\n' \
       f'Валюта расчета - {CityInfoState.data[message.chat.id]["currency"]}\n' \
       f'Необходимость фотографий - {CityInfoState.data[message.chat.id]["need_photo"]}\n' \
       f'Количество фотографий - {CityInfoState.data[message.chat.id]["count_photo"]}\n' \
       f'Количество дней в отеле - {CityInfoState.data[message.chat.id]["days_in_hotel"]}'
    bot.send_message(message.chat.id, text)
    request_hotels(message)
    bot.register_next_step_handler(message, show_hotels(message))


def show_hotels(message: Message) -> None:
    if CityInfoState.data[message.chat.id]['criterion'] == 'low_price':
        hotels_to_show = sorted(search_lowprice_highprice(), key=lambda x: x['price'])
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
        for i in range(config.max_hotels_count):
            bot.send_message(message.chat.id, sending_hotels_message(hotels_to_show, i, message))
    elif CityInfoState.data[message.chat.id]['criterion'] == 'high_price':
        hotels_to_show = sorted(search_lowprice_highprice(), key=lambda x: x['price'], reverse=True)
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
        for i in range(config.max_hotels_count):
            bot.send_message(message.chat.id, sending_hotels_message(hotels_to_show, i))
    elif CityInfoState.data[message.chat.id]['criterion'] == 'best_deal':
        hotels_to_show = sorted(search_bestdeal(message), key=lambda x: x['distance'])
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
        for i in range(config.max_hotels_count):
            bot.send_message(message.chat.id, sending_hotels_message(hotels_to_show, i))


def sending_hotels_message(hotels: list, index: int, message) -> str:
    full_price = round((hotels[index]['price']) * CityInfoState.data[message.chat.id]['days_in_hotel'])
    text = f"🏨Наименование: {hotels[index]['name']}\n" \
           f"⭐Рейтинг: {hotels[index]['starrating']}\n" \
           f"🌎Адрес: {hotels[index]['address']}\n" \
           f"💴Цена за сутки: {hotels[index]['price']} {CityInfoState.data[message.chat.id]['currency']}\n" \
           f"💰Цена за {CityInfoState.data[message.chat.id]['days_in_hotel']} суток: {full_price} {CityInfoState.data[message.chat.id]['currency']}\n" \
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
                    current_cost = i.get('ratePlan', []).get('price', []).get('exactCurrent', 0)
                    current_dist = i.get('landmarks', [])[0].get('distance', '')
                    if current_cost < float(CityInfoState.data[message.chat.id]['max_cost']) and \
                        float(CityInfoState.data[message.chat.id]['distance_from_center']) > current_dist:
                        hotels_list_bestdeal.append({'id': i['id'], 'name': i['name'], 'starrating': i['starRating'],
                                            'address': i.get('address', []).get('streetAddress'),
                                            'distance': i.get('landmarks', [])[0].get('distance', ''),
                                            'price': i.get('ratePlan', []).get('price', []).get('exactCurrent', 0)})

                return hotels_list_bestdeal
            except AttributeError:
                hotels_list_bestdeal.append(dict())
                return hotels_list_bestdeal







