from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot
from states.city_to_find_info import CityInfoState
from datetime import date, timedelta
from telebot.types import Message
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

MY_STEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(commands=['calendar'])
def get_arrival_data(message: Message) -> None:
    bot.send_message(message.chat.id, 'Записал! Введите дату заезда: ')
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
    bot.send_message(message.chat.id,
                     f"Выберите {MY_STEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal_arrival_data(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today() + timedelta(days=1)).process(call.data)
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
        bot.register_next_step_handler(call.message, get_departure_data(call.message))


@bot.message_handler(commands=['calendar_2'])
def get_departure_data(message: Message) -> None:
    bot.send_message(message.chat.id, 'Записал! Теперь введите дату отъезда: ')
    calendar, step = DetailedTelegramCalendar(calendar_id=2,
                                              ).build()
    bot.send_message(message.chat.id,
                     f"Выберите {MY_STEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal_departure_data(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=CityInfoState.data[call.message.chat.id]['arrival_date']
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
        CityInfoState.data[call.message.chat.id]['departure_data'] = result
        CityInfoState.data[call.message.chat.id]['days_in_hotel'] = (CityInfoState.data[call.message.chat.id]['departure_data'] -
                                                                     CityInfoState.data[call.message.chat.id]['arrival_date']).days
        currency = InlineKeyboardMarkup()
        currency.add(InlineKeyboardButton(text='RUB', callback_data='RUB'))
        currency.add(InlineKeyboardButton(text='USD', callback_data='USD'))
        currency.add(InlineKeyboardButton(text='EUR', callback_data='EUR'))
        bot.send_message(call.from_user.id, 'Выберите валюту рассчета', reply_markup=currency)

