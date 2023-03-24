import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration
import logging

sentry_logging = LoggingIntegration(
    level=logging.INFO,
    event_level=logging.INFO

)
sentry_sdk.init(
    dsn="https://677640d906f047079f0dc9a03ea5340e@o4504889429196800.ingest.sentry.io/4504889433980928",
    traces_sample_rate=1.0,
    integrations=[
        sentry_logging]
)
