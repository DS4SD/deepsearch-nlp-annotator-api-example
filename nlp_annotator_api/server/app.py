import logging
from nlp_annotator_api.server.middleware.redis_cache import redis_cache_factory
import os

import aiohttp.web
from connexion import AioHttpApp

from nlp_annotator_api.config.config import conf
from nlp_annotator_api.config.logging import setup_logging
from nlp_annotator_api.server.middleware.statsd_middleware import StatsdMiddleware
from nlp_annotator_api.server.signals.statsd_client import statsd_client_factory

setup_logging()

access_log = logging.getLogger("nlp_annotator_api.access")

_file_dir = os.path.dirname(__file__)

app = AioHttpApp(
    __name__, specification_dir=os.path.join(_file_dir, "..", "resources", "schemas"),
    server_args=dict(
        client_max_size=8 * 1024**2
    )  
)

app.add_api("openapi.yaml", pass_context_arg_name="request")

aiohttp_app: aiohttp.web.Application = app.app

aiohttp_app.cleanup_ctx.append(statsd_client_factory(conf.statsd))
aiohttp_app.cleanup_ctx.append(redis_cache_factory(conf))

aiohttp_app.middlewares.append(StatsdMiddleware())

if __name__ == "__main__":
    app.run(access_log=access_log)
