import schedule
import time
from datetime import datetime
from tbot import tg_poster
from constants import postgresql, PARSED_WEBSITES


PARSE_EVERY_MINUTES = 10


def do_post_in_telegram():
    print(f'Телеграм оповещения стартовали: {datetime.now()}')
    posts = postgresql.get_all_not_posted_flats(list(map(lambda x: x.parser_sub, PARSED_WEBSITES)))
    if posts:
        for post in posts:
            post_message = f'<b>Цена:</b> {post[2]} BYN\n'
            post_message += f'<b>Описание:</b> {post[4]}\n\n'
            post_message += '\n'.join(list(map(lambda el: el, post[6].split(',')[:6])))
            tg_poster.send_tg_post(post_message)
            time.sleep(5)
    postgresql.update_is_posted_state(list(map(lambda el: el[7], posts)))


schedule.every(PARSE_EVERY_MINUTES).minutes.do(do_post_in_telegram)

while True:
    schedule.run_pending()
    time.sleep(1)
