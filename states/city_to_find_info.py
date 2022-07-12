from telebot.handler_backends import State, StatesGroup


class CityInfoState:
    city = None
    destination_id = None
    arrival_date = None
    departure_date = None
    days_in_hotel = None
    currency = None
    need_photo = None
    count_photo = None
    final_state = None
