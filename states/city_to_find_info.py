from telebot.handler_backends import State, StatesGroup


class CityInfoState(StatesGroup):
    data = dict()
    city = State()
    arrival_date = State()
    departure_date = State()
    criterion = State()
    currency = State()
    need_photo = State()
    count_photo = State()
    distance_from_center = State()
    max_cost = State()
    hotels_count = State()
