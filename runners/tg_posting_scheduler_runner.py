import schedule
import time
import random
# from constants import USED_PARSERS
import threading

from datetime import datetime

import tg_poster
from dbs.dbs import PostgresqlDB

# from runners.tasks_scheduler_runner import postgres
postgres = PostgresqlDB()
PARSE_EVERY_MINUTES = 10


def do_post_in_telegram():
    print(f'Телеграм оповещения стартовали: {datetime.now()}')
    parser_names = ("gohome_by", "realt_by")
    posts = postgres.get_all_not_posted_flats(parser_names)
    for post in posts:
        post_message = f'<b>Цена:</b> {post[2]} BYN\n'
        post_message += f'<b>Описание:</b> {post[4]}\n\n'
        post_message += '\n'.join(list(map(lambda el: el, post[6].split(',')[:6])))
        tg_poster.send_tg_post(post_message)
        time.sleep(5)
    postgres.update_is_posted_state(list(map(lambda el: el[7], posts)))

schedule.every(PARSE_EVERY_MINUTES).seconds.do(do_post_in_telegram)


while True:
    schedule.run_pending()
    time.sleep(1)
