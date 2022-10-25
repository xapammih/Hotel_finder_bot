from telebot.types import Message
from loader import bot
import sqlite3


db = sqlite3.connect('bot_history.db', check_same_thread=False)
sql = db.cursor()


@bot.message_handler(commands=['history'])
def bot_history(message: Message):
    bot.send_message(message.from_user.id, 'История поиска: ')
    show_database(message)


def create_table():
    """
    Функция создает базу данных hotels с полями chat_id и hotel_info(текст из запроса)
    :return:
    """
    sql.execute("""CREATE TABLE IF NOT EXISTS hotels (
    chat_id INT,
    hotel_info TEXT
    )""")
    db.commit()


def database_worker(message: Message, text: str) -> None:
    """
    Функция заполняет поля базы данных
    :param message:
    :param text:
    :return:
    """
    sql.execute(f"INSERT INTO hotels VALUES(?, ?)", (message.chat.id, text))
    db.commit()


def show_database(message: Message) -> None:
    """
    Функция выводит историю поиска из базы данных hotels
    :param message:
    :return:
    """
    show_db_select = sql.execute(f"SELECT hotel_info FROM hotels WHERE chat_id = (?)", (message.chat.id, ))
    for index, value in enumerate(show_db_select):
        bot.send_message(message.chat.id, value)
        if index == 10:
            break
    db.close()
