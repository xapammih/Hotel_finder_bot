from utils.set_bot_commands import set_default_commands
from loader import bot
import handlers
from telebot.custom_filters import StateFilter
from utils.API.requests import main_request


if __name__ == "__main__":

    try:
        bot.add_custom_filter(StateFilter(bot))
        set_default_commands(bot)
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    # except Exception as r:
    #     print("Непридвиденная ошибка: ", r)
    # finally:
    #     print("Здесь всё закончилось")





