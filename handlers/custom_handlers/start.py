from telebot.types import Message
from loader import bot
from states import city_to_find_info


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    print(message.from_user.id)
    city_to_find_info.CityInfoState.data[message.from_user.id] = {'city': None, 'destination_id': None, 'arrival_date': None, 'departure_date': None,
                        'days_in_hotel': None, 'criterion': None, 'currency': None, 'need_photo': None,
                        'count_photo': None, 'hotels_count': None, 'distance_from_center': None,
                        'max_cost': None, 'min_cost': None}
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\n"
                          f"Для поиска гостиницы наберите команду /search\n"
                          f"Для справки наберите команду /help")

