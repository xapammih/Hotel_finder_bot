from utils.set_bot_commands import set_default_commands
from loader import bot
from handlers.default_handlers import start, echo, help, history
from utils.API.requests import main_request

if __name__ == "__main__":
    main_request()
    try:
        set_default_commands(bot)
        bot.polling(none_stop=True)
    except ConnectionError as e:
        print('Ошибка соединения: ', e)
    except Exception as r:
        print("Непридвиденная ошибка: ", r)
    finally:
        print("Здесь всё закончилось")
