from telebot.handler_backends import State, StatesGroup


class CityInfoState(StatesGroup):
    city = State()
    arrival_date = State()
    departure_date = State()
    currency = State()
    need_photo = State()
    count_photo = State()
