from utils.API.requests import request_hotels
from loader import bot
from states.city_to_find_info import CityInfoState
from telebot.types import Message
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import json
import re


@bot.message_handler()
def show_hotels_func(message: Message) -> None:
    request_hotels()
