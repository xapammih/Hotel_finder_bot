from loader import bot
from telebot.types import Message
import json
from utils.API.requests import request_city, request_hotels, request_hotels_photo, request_rub_currency
import re
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from states.city_to_find_info import CityInfoState
from keyboards.inline import dialog_keyboards, calendar
from config_data import config
from telebot import types
from loguru import logger
import requests
from database.history_database import database_worker as db


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
    """
    Функция ловит команду search, запрашивает интересующий город.
    Создает словарь с ключом chat.id и значением-словарем, который заполняется поступающей далее информацией.
    :param message:
    :return:
    """
    logger.debug('Начинаем работу!')
    CityInfoState.data[message.chat.id] = {'city': None, 'destination_id': None, 'arrival_date': None, 'departure_date': None,
                        'days_in_hotel': None, 'criterion': None, 'currency': None, 'need_photo': None,
                        'count_photo': None, 'hotels_count': None, 'distance_from_center': None,
                        'max_cost': None, 'min_cost': None}
    bot.send_message(message.from_user.id, f'Введите город, в какой вы бы хотели отправиться: ')
    bot.register_next_step_handler(message, city)


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


def city_markup(city_to_find: str):
    """
    Функция делает запрос к API города, формирует и возвращает клавиатуру с вариантами ответа интересующего города
    :param city_to_find:
    :return:
    """
    cities = city_founding(city_to_find)
    destinations = InlineKeyboardMarkup()
    for city in cities:
        destinations.add(InlineKeyboardButton(text=city['city_name'],
                                              callback_data=f'id_{city["destination_id"]}'))
    return destinations


def city(message):
    """
    Уточняющая город функция
    :param message:
    :return:
    """
    bot.send_message(message.from_user.id, 'Уточните, пожалуйста:', reply_markup=city_markup(message.text))


@bot.callback_query_handler(func=lambda call: call.data.startswith('id_'))
def city_inline_callback(call) -> None:
    """
    Колбэк города, записывает город в дата-словарь, перенаправляет на календарь с выбором даты заезда
    :param call:
    :return:
    """
    for i in call.message.reply_markup.keyboard:
        for keyboard in i:
            if keyboard.callback_data == call.data:
                CityInfoState.data[call.message.chat.id]['city'] = keyboard.text
                logger.debug(f'Выбран город: {keyboard.text}')
    dest_id = call.data[3:]
    CityInfoState.data[call.message.chat.id]['destination_id'] = dest_id
    bot.send_message(call.message.chat.id, 'Записал! Введите дату заезда: ')
    calendar.get_arrival_data(call.message)
    bot.set_state(user_id=call.from_user.id, state=CityInfoState.arrival_date, chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data in ['EUR', 'RUB', 'USD'])
def get_currency(call) -> None:
    """
    Колбэк валюты
    :param call:
    :return:
    """
    CityInfoState.data[call.message.chat.id]['currency'] = call.data
    logger.debug(f'Выбрана валюта: {call.data}')
    bot.send_message(call.message.chat.id, 'По каким критериям выбираем отель? ',
                     reply_markup=dialog_keyboards.get_criterion_keyboard())
    bot.set_state(user_id=call.from_user.id, state=CityInfoState.criterion, chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data in ['low_price', 'high_price', 'best_deal'])
def criterion_callback(call) -> None:
    """
    Колбэк ценового критерия
    :param call:
    :return:
    """
    CityInfoState.data[call.message.chat.id]['criterion'] = call.data
    logger.debug(f'Выбран ценовой критерий: {call.data}')
    bot.set_state(user_id=call.from_user.id, state=CityInfoState.need_photo, chat_id=call.message.chat.id)
    bot.send_message(call.message.chat.id, 'Нужны ли фото отеля?', reply_markup=dialog_keyboards.need_photos_keyboard())


@bot.callback_query_handler(func=lambda call: call.data in ['нужны_фото', 'не_нужны_фото'])
def need_photo_callback(call) -> None:
    """
    Колбэк необходимости фотографий отеля, если нужны-направляем на запрос кол-ва фотографий, если нет-выводим финальное сообщение
    и список отеля. Также идет ветвление на bestdeal и остальные критерии цены
    :param call:
    :return:
    """
    if call.data == 'нужны_фото':
        CityInfoState.data[call.message.chat.id]['need_photo'] = call.data
        logger.debug(f'Выбрана необходимость фотографий: {call.data}')
        bot.set_state(user_id=call.from_user.id, state=CityInfoState.count_photo, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Сколько фотографий отображаем? ',
                         reply_markup=dialog_keyboards.count_photo_keyboard())
    else:
        CityInfoState.data[call.message.chat.id]['need_photo'] = 'нет'
        CityInfoState.data[call.message.chat.id]['count_photo'] = 0
        logger.debug(f'Выбрана необходимость фотографий: {call.data}')
        if CityInfoState.data[call.message.chat.id]['criterion'] == 'best_deal':
            bot.set_state(user_id=call.from_user.id, state=CityInfoState.max_cost, chat_id=call.message.chat.id)
            bot.send_message(call.message.chat.id, 'Введите максимальную цену за сутки: ')
        else:
            ending_message(call.message)


@bot.callback_query_handler(func=lambda call: call.data in ['1_photo', '2_photo', '3_photo',
                                                            '4_photo', '5_photo', '6_photo'])
def count_photo_callback(call) -> None:
    """
    Колбэк кол-ва фотографий отеля
    :param call:
    :return:
    """
    CityInfoState.data[call.message.chat.id]['count_photo'] = call.data[0]
    logger.debug(f'Выбрано количество фотографий: {call.data[0]}')
    if CityInfoState.data[call.message.chat.id]['criterion'] == 'best_deal':
        bot.set_state(user_id=call.from_user.id, state=CityInfoState.max_cost, chat_id=call.message.chat.id)
        bot.send_message(call.message.chat.id, 'Введите максимальную цену за сутки: ')
    else:
        ending_message(call.message)


@bot.message_handler(state=CityInfoState.max_cost)
def bestdeal_price_info(message: Message):
    """
    Запрос максимальной цены для критерия bestdeal
    :param message:
    :return:
    """
    if CityInfoState.currency == 'RUB':
        CityInfoState.data[message.from_user.id]['max_cost'] = int(message.text)
        logger.debug(f'Выбрана максимальная цена критерия bestdeal: {message.text}')
    else:
        CityInfoState.data[message.from_user.id]['max_cost'] = message.text
        logger.debug(f'Выбрана максимальная цена критерия bestdeal: {message.text}')
    bot.set_state(user_id=message.from_user.id, state=CityInfoState.distance_from_center, chat_id=message.chat.id)
    bot.send_message(message.chat.id, 'Введите максимальное расстояние от центра: ')


@bot.message_handler(state=CityInfoState.distance_from_center)
def bestdeal_distance_info(message: Message):
    """
    Запрос расстояния от центра для критерия bestdeal
    :param message:
    :return:
    """
    CityInfoState.data[message.from_user.id]['distance_from_center'] = message.text
    logger.debug(f'Выбрана максимальное расстояние от центра критерия bestdeal: {message.text}')
    ending_message(message)


def ending_message(message: Message) -> None:
    """
    Формирование и отправка финального сообщения с собранными данными
    :param message:
    :return:
    """
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
    """
    Функция, выводящая в телеграм список отелей(максимум 10)
    :param message:
    :return:
    """
    if CityInfoState.data[message.chat.id]['criterion'] == 'low_price':
        hotels_to_show = sorted(search_lowprice_highprice(message), key=lambda x: x['price'])
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        else:
            bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
            for i in range(config.max_hotels_count):
                if int(CityInfoState.data[message.chat.id]['count_photo']) != 0:
                    bot.send_media_group(message.chat.id, search_photos(message, hotels_to_show[i]))
                text = sending_hotels_message(hotels_to_show, i, message)
                db(message, text)
                bot.send_message(message.chat.id, text)
            bot.delete_state(message.from_user.id, message.chat.id)
    elif CityInfoState.data[message.chat.id]['criterion'] == 'high_price':
        hotels_to_show = sorted(search_lowprice_highprice(message), key=lambda x: x['price'], reverse=True)
        if len(hotels_to_show) == 0:
            bot.send_message(message.chat.id, 'Ничего не найдено.')
        else:
            bot.send_message(message.chat.id, 'Вот что мне удалось найти по вашему запросу:\n')
            for i in range(config.max_hotels_count):
                if int(CityInfoState.data[message.chat.id]['count_photo']) != 0:
                    bot.send_media_group(message.chat.id, search_photos(message, hotels_to_show[i]))
                text = sending_hotels_message(hotels_to_show, i, message)
                db(message, text)
                bot.send_message(message.chat.id, text)
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
                text = sending_hotels_message(hotels_to_show, i, message)
                db(message, text)
                bot.send_message(message.chat.id, text)
            bot.delete_state(message.from_user.id, message.chat.id)


def sending_hotels_message(hotels: list, index: int, message: Message) -> str:
    """
    Функция, возвращающая текст для вывода в телеграм одного отеля(без фоток)
    :param hotels:
    :param index:
    :param message:
    :return:
    """
    full_price = round((hotels[index]['price']) * CityInfoState.data[message.chat.id]['days_in_hotel'])
    # if CityInfoState.data[message.chat.id]['currency'] == 'RUB':
    #     full_price *= round(request_rub_currency())
    #     dayly_price = round(hotels[index]['price'] * request_rub_currency())
    # else:
    dayly_price = hotels[index]['price']
    text = f"🏨Наименование: {hotels[index]['name']}\n" \
           f"⭐Рейтинг: {hotels[index]['starrating']}\n" \
           f"🌎Адрес: {hotels[index]['address']}\n" \
           f"💴Цена за сутки: {dayly_price} {CityInfoState.data[message.chat.id]['currency']}\n" \
           f"💰Цена за {CityInfoState.data[message.chat.id]['days_in_hotel']} суток: " \
           f"{full_price} {CityInfoState.data[message.chat.id]['currency']}\n" \
           f"➡️Расстояние до центра: {hotels[index]['distance']}"
    return text



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
                                    'price': i.get('ratePlan', []).get('price', []).get('exactCurrent', 0)})
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
                hotels_photo_lst.append(types.InputMediaPhoto(temp))
        else:
            break
    return hotels_photo_lst



