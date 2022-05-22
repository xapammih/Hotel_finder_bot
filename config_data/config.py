import os
from dotenv import load_dotenv, find_dotenv

# if not find_dotenv():
#     exit('Переменные окружения не загружены т.к отсутствует файл .env')
# else:
#     load_dotenv()


token = '5233020354:AAG0YyzhA3e5oM3MFAemsGcaBCH19S04iFY'
rapidapi_key = "e800e098c4msh474c79e3bce3792p154ddajsn238a4e9968f5"

BOT_TOKEN = os.getenv('BOT_TOKEN')
RAPID_API_KEY = os.getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ('history', "История")
)
