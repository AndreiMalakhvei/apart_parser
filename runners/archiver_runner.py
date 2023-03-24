import schedule
from constants import postgresql
import requests
from tqdm import tqdm
import time
from datetime import datetime
import sentry_logger

START_TIME = '01:00'


def start_archiver() -> None:
    print(f'Архиватор стартовал: {datetime.now()}')
    records_to_archieve = []
    active_records = postgresql.get_not_archived()
    for record in tqdm(active_records,desc='Archiver checks active links'):
        response = requests.get(record[1], allow_redirects=False)
        if 300 <= response.status_code <= 404:
            records_to_archieve.append(record[0])
    if records_to_archieve:
        postgresql.update_is_archived_state(records_to_archieve)

schedule.every().day.at(START_TIME).do(start_archiver)

while True:
    schedule.run_pending()
    time.sleep(1)
