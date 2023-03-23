import schedule
import time
from datetime import datetime

from constants import postgresql, PARSED_WEBSITES
from tbot.secret_key_bot import BOT_SECRET_KEYS

from tbot.tg_poster import send_tg_post

POST_EVERY_MINUTES = 30
SUB_POST_EVERY_MINUTES = 10
REPORT_GROUP_ID = BOT_SECRET_KEYS['GROUP_ID']

def do_post_in_telegram() -> None:
    print(f'Телеграм оповещения стартовали: {datetime.now()}')
    posts = postgresql.get_all_not_posted_flats(list(map(lambda x: x.parser_sub, PARSED_WEBSITES)))
    if posts:
        for post in posts:
            post_message = f'<b>Цена:</b> {post[3]} BYN\n'
            post_message += f'<b>Описание:</b> {post[4]}\n\n'
            post_message += '\n'.join(list(map(lambda el: el, post[17].strip("{}").split(',')[:6])))
            send_tg_post(REPORT_GROUP_ID, post_message)
            time.sleep(5)
    postgresql.update_is_posted_state(list(map(lambda el: el[7], posts)))

def post_to_subscribed() -> None:
    print(f'Стартовали оповещения по платным подпискам: {datetime.now()}')
    subscribers = postgresql.get_subscribers()
    for subscriber in subscribers:
        print(subscriber[0])
        posts = postgresql.get_posts_for_subscriber(subscriber)
        print('posts:', posts)
        if posts:
            for post in posts:
                post_message = f'<b>Цена:</b> {post[3]} BYN\n'
                post_message += f'<b>Описание:</b> {post[4]}\n\n'
                post_message += '\n'.join(list(map(lambda el: el, post[17].strip("{}").split(',')[:6])))
                send_tg_post(subscriber[0], post_message)
                time.sleep(5)



schedule.every(POST_EVERY_MINUTES).minutes.do(do_post_in_telegram)
schedule.every(SUB_POST_EVERY_MINUTES).seconds.do(post_to_subscribed)

while True:
    schedule.run_pending()
    time.sleep(1)
