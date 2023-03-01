import schedule
import time
import threading
from datetime import datetime
from constants import PARSED_WEBSITES

PARSE_EVERY_MINUTES = 3

def parse_all():
    for website in PARSED_WEBSITES:
        thread = threading.Thread(target=website.run(1,2))
        thread.start()
        print(f'Парсер {website.parser_sub} стартовал: {datetime.now()}')

schedule.every(PARSE_EVERY_MINUTES).minutes.do(parse_all)


while True:
    schedule.run_pending()
    time.sleep(1)
