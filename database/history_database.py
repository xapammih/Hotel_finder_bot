from telebot.types import Message
from loader import bot
import sqlite3
from states.city_to_find_info import CityInfoState

db = sqlite3.connect('bot_history.db')
sql = db.cursor()


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    bot.send_message(message.from_user.id, 'История поиска: ')
    show_database(message)


def database_worker(message: Message, text):
    sql.execute("""CREATE TABLE IF NOT EXISTS hotels (
    chat_id INT,
    hotel_info TEXT
    )""")
    db.commit()
    # sql.execute(f"INSERT INTO hotels VALUES(?)", (CityInfoState.data[message.chat.id]))
    sql.execute(f'INSERT INTO hotels VALUES(?)', (text))
    db.commit()


def show_database(message: Message):
    for value in sql.execute(f"SELECT * FROM hotels WHERE chat_id = {CityInfoState.data[message.chat.id]}"):
        bot.send_message(message.chat.id, value)
    db.close()