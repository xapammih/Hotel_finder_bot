from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot
from states.city_to_find_info import CityInfoState
from datetime import date, timedelta
from telebot.types import Message
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
from loguru import logger

MY_STEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}


def get_arrival_data(message: Message):
    """
    Функция, формирующая календарь для даты приезда
    :param message:
    :return:
    """
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
    bot.send_message(message.chat.id,
                     f"Выберите {MY_STEP[step]}",
                     reply_markup=calendar)
    return DetailedTelegramCalendar


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal_arrival_data(call):
    """
    Колбэк календаря с датой приезда
    :param call:
    :return:
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=1,
                                                 min_date=date.today() + timedelta(days=1)).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MY_STEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        CityInfoState.data[call.message.chat.id]['arrival_date'] = result
        logger.debug(f'Выбрана дата заезда: {result}')
        bot.send_message(call.message.chat.id, 'Записал! Теперь введите дату отъезда: ')
        get_departure_data(call.message)


def get_departure_data(message: Message):
    """
    Функция, формирующая календарь для даты отъезда
    :param message:
    :return:
    """
    calendar, step = DetailedTelegramCalendar(calendar_id=2,
                                              ).build()
    bot.send_message(message.chat.id,
                     f"Выберите {MY_STEP[step]}",
                     reply_markup=calendar)
    return DetailedTelegramCalendar


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal_departure_data(call):
    """
    Колбэк календаря с датой отъезда, также запрашивает валюту расчета
    :param call:
    :return:
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=2,
                                                 min_date=CityInfoState.data[call.message.chat.id]['arrival_date']
                                                                         + timedelta(days=1)).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MY_STEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        CityInfoState.data[call.message.chat.id]['departure_date'] = result
        logger.debug(f'Выбрана дата отъезда: {result}')
        CityInfoState.data[call.message.chat.id]['days_in_hotel'] = (CityInfoState.data[call.message.chat.id]['departure_date'] -
                                                                     CityInfoState.data[call.message.chat.id]['arrival_date']).days
        logger.debug(f'Кол-во дней в отеле: {CityInfoState.data[call.message.chat.id]["days_in_hotel"]}')
        bot.set_state(user_id=call.from_user.id, state=CityInfoState.currency, chat_id=call.message.chat.id)
        currency = InlineKeyboardMarkup()
        currency.add(InlineKeyboardButton(text='RUB', callback_data='RUB'))
        currency.add(InlineKeyboardButton(text='USD', callback_data='USD'))
        currency.add(InlineKeyboardButton(text='EUR', callback_data='EUR'))
        bot.send_message(call.from_user.id, 'Выберите валюту расчета', reply_markup=currency)

