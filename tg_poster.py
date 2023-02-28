import telebot


# https://t.me/realtyservbot
bot = telebot.TeleBot('6231031566:AAGMcTuN7ItfFf_qCenW2sO1Lkk37500P9U')
REPORT_GROUP_ID = '-1001830842652'

def send_tg_post(message):
    bot.send_message(REPORT_GROUP_ID, message, parse_mode='html')
