import telebot
from secret_key_bot import BOT_SECRET_KEYS


# https://t.me/realtyservbot
bot = telebot.TeleBot(BOT_SECRET_KEYS['TELEBOT_ID'])
REPORT_GROUP_ID = BOT_SECRET_KEYS['GROUP_ID']

def send_tg_post(message):
    bot.send_message(REPORT_GROUP_ID, message, parse_mode='html')
