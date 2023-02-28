import schedule
import time
import threading
from datetime import datetime

from dbs.dbs import PostgresqlDB
from parsers.parsers import RealtByParser, GoHomeParser
from websites.basewebsitehandler import WebSiteHandler

postgres = PostgresqlDB()

realt = WebSiteHandler()
parser = RealtByParser()

def handle_realt():
    urls = realt.get_urls_list(parser, page_to=2)
    flats = realt.build_flats_list(parser, urls)
    realt.save_to_db_no_firestorage(flats, postgres)

gohome = WebSiteHandler()
parser2 = GoHomeParser()

def handle_gohome():
    urls = gohome.get_urls_list(parser2, page_to=2)
    flats = gohome.build_flats_list(parser2, urls)
    gohome.save_to_db_no_firestorage(flats, postgres)

USED_PARSERS = [handle_gohome, handle_realt]


PARSE_EVERY_MINUTES = 30

def parse_all():
    for parser in USED_PARSERS:
        thread = threading.Thread(target=parser)
        thread.start()
        print(f'Парсер {parser.__name__} стартовал: {datetime.now()}')


schedule.every(PARSE_EVERY_MINUTES).seconds.do(parse_all)


while True:
    schedule.run_pending()
    time.sleep(1)
