from telebot.types import Message
from loader import bot


@bot.message_handler(commands=['start'])
def bot_start(message: Message):
    bot.reply_to(message, f"Привет, {message.from_user.full_name}!\n"
                          f"Для поиска гостиницы наберите команду /search\n"
                          f"Для справки наберите команду /help")

