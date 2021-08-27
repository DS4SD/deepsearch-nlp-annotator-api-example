import logging

import statsd

logger = logging.getLogger(__name__)


def statsd_client_factory(statsd_kwargs):
    async def statsd_client(app_instance):
        logger.debug("Adding statsd client")

        client = statsd.StatsClient(**statsd_kwargs)

        app_instance['statsd_client'] = client

        yield

    return statsd_client
