from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
import json
import requests

storage = StateMemoryStorage()
bot = TeleBot(token=config.token, state_storage=storage)
