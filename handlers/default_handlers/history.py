from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    bot.send_message(message.from_user.id, 'История поиска: ')