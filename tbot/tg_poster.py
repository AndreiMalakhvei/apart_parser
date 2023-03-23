import telebot
from tbot.secret_key_bot import BOT_SECRET_KEYS


# https://t.me/realtyservbot
bot = telebot.TeleBot(BOT_SECRET_KEYS['TELEBOT_ID'])
REPORT_GROUP_ID = BOT_SECRET_KEYS['GROUP_ID']


def send_tg_post(id, message):
    bot.send_message(id, message, parse_mode='html')



