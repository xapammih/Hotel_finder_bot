from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    bot.send_message(message.from_user.id, 'Инструкция к боту: \n'
                                           'Для начала работы с ботом введите команду /start \n'
                                           'Опрос /survey\n'
                                           'Вывести справку /help')