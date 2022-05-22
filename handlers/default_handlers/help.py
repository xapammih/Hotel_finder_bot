from telebot.types import Message

from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: Message):
    bot.send_message(message.from_user.id, 'Инструкция к боту: \n'
                                           'Для поиска лучшего предложения по отелям введите команду /bestdeal\n'
                                           'Для поиска самого дешевого отеля введите команду /lowprice\n'
                                           'Для просмотра истории поиска введите команду /history')