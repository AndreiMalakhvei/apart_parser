from parsers.parsers import RealtBS4Parser, GoHomeBS4Parser
from dbs.dbs import PostgresqlDB
from websites.basewebsitehandler import WebSiteHandler

postgresql = PostgresqlDB()

realt_handler = WebSiteHandler(RealtBS4Parser(), postgresql)
gohome_handler = WebSiteHandler(GoHomeBS4Parser(), postgresql)

PARSED_WEBSITES = [realt_handler, gohome_handler]
