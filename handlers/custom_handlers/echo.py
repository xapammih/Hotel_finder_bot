from telebot.types import Message
from loader import bot


@bot.message_handler()
def bot_echo(message: Message):
    bot.reply_to(message, "Эхо без состояния или фильтра.\nСообщение:"
                          f"{message.text}")
