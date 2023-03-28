from parsers.parsers import RealtBS4Parser, GoHomeBS4Parser
from dbs.dbs import PostgresqlDB
from websites.basewebsitehandler import WebSiteHandler


postgresql = PostgresqlDB()

realt_handler = WebSiteHandler(RealtBS4Parser(), postgresql)
gohome_handler = WebSiteHandler(GoHomeBS4Parser(), postgresql)

# PARSED_WEBSITES = [realt_handler, gohome_handler]
PARSED_WEBSITES = [gohome_handler]

import sentry_sdk
sentry_sdk.init(
    dsn="https://677640d906f047079f0dc9a03ea5340e@o4504889429196800.ingest.sentry.io/4504889433980928",


    traces_sample_rate=1.0
)
