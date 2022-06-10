from telegram_bot_calendar import DetailedTelegramCalendar
from loader import bot
from handlers.custom_handlers.get_city import get_currency
from states.city_to_find_info import CityInfoState
from datetime import date, timedelta
from telebot.types import ReplyKeyboardRemove
from telebot.types import Message


MY_STEP = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(state=CityInfoState.arrival_date)
def get_arrival_data(message: Message) -> None:
    bot.send_message(message.chat.id, 'Записал! Введите дату заезда: ')
    calendar, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).build()
    bot.send_message(message.chat.id,
                     f"Выберите {MY_STEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def cal_arrival_data(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=1, min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MY_STEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['arrival_data'] = result
        bot.set_state(str(call.message.chat.id), CityInfoState.departure_date)
        bot.register_next_step_handler(call.message, get_departure_data(call.message))


# min_date=CityInfoState.arrival_date + timedelta(days=1)
@bot.message_handler(state=CityInfoState.departure_date)
def get_departure_data(message: Message) -> None:
    bot.send_message(message.chat.id, 'Записал! Теперь введите дату отъезда: ')
    calendar, step = DetailedTelegramCalendar(calendar_id=2,
                                              ).build()
    bot.send_message(message.chat.id,
                     f"Выберите {MY_STEP[step]}",
                     reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def cal_departure_data(call):
    result, key, step = DetailedTelegramCalendar(calendar_id=2, min_date=date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f"Выберите {MY_STEP[step]}",
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f"Вы выбрали {result}",
                              call.message.chat.id,
                              call.message.message_id)
        with bot.retrieve_data(call.from_user.id, call.message.chat.id) as data:
            data['departure_data'] = result
            # data['days_in_hotel'] = (CityInfoState.departure_date - CityInfoState.arrival_date).days
        bot.set_state(str(call.message.chat.id), CityInfoState.currency)
        bot.register_next_step_handler(call.message, get_currency(call.message))