from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.API.requests import city_founding


def get_criterion_keyboard():
    criterion_buttons = InlineKeyboardMarkup()
    criterion_buttons.add(InlineKeyboardButton(text='Минимальная цена', callback_data='low_price'))
    criterion_buttons.add(InlineKeyboardButton(text='Максимальная цена', callback_data='high_price'))
    criterion_buttons.add(InlineKeyboardButton(text='Лучшее предложение!', callback_data='best_deal'))
    return criterion_buttons


def need_photos_keyboard():
    is_need_photo_buttons = InlineKeyboardMarkup()
    is_need_photo_buttons.add(InlineKeyboardButton(text='Да', callback_data='нужны_фото'))
    is_need_photo_buttons.add(InlineKeyboardButton(text='Нет', callback_data='не_нужны_фото'))
    return is_need_photo_buttons


def count_photo_keyboard():
    count_photo_buttons = InlineKeyboardMarkup()
    count_photo_buttons.add(InlineKeyboardButton(text='1', callback_data='1_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='2', callback_data='2_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='3', callback_data='3_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='4', callback_data='4_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='5', callback_data='5_photo'))
    count_photo_buttons.add(InlineKeyboardButton(text='6', callback_data='6_photo'))
    return count_photo_buttons


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