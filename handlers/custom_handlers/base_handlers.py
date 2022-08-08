from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot
from handlers.custom_handlers.get_city import city


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\n"
                          f"Для поиска гостиницы наберите команду /search\n"
                          f"Для справки наберите команду /help")


@bot.message_handler(commands=['search'])
def search(message: Message) -> None:
    bot.send_message(message.from_user.id, f'Введите город, в какой вы бы хотели отправиться: ')
    bot.register_next_step_handler(message, city)


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    text = [f'/{command} - {desk}' for command, desk in DEFAULT_COMMANDS]
    bot.reply_to(message, '\n'.join(text))


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    bot.send_message(message.from_user.id, 'История поиска: ')







@bot.message_handler()
def bot_echo(message: Message):
    bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение:"
                          f"{message.text}")
