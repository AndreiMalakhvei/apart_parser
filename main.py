from dbs.dbs import FireStorage, PostgresqlDB
from parsers.parsers import RealtByParser, GoHomeParser
from websites.basewebsitehandler import WebSiteHandler
from threading import Thread

firestorage = FireStorage()
postgres = PostgresqlDB()

realt = WebSiteHandler()
parser = RealtByParser()

def handle_realt():
    urls = realt.get_urls_list(parser, page_to=0)
    flats = realt.build_flats_list(parser, urls)
    realt.save_to_db_no_firestorage(flats, postgres)

gohome = WebSiteHandler()
parser2 = GoHomeParser()

def handle_gohome():
    urls = gohome.get_urls_list(parser2, page_to=1)
    flats = gohome.build_flats_list(parser2, urls)
    gohome.save_to_db_no_firestorage(flats, postgres)

t1 = Thread(target=handle_realt)
t2 = Thread(target=handle_gohome)

t1.start()
t2.start()

t1.join()
t2.join()

print("Done!")


