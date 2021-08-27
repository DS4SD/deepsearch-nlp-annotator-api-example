import logging
from concurrent.futures.process import ProcessPoolExecutor

logger = logging.getLogger(__name__)


def process_pool_factory(num_workers: int):
    async def process_pool(app_instance):

        logger.debug("Setting up process pool with %r workers", num_workers)

        pool = ProcessPoolExecutor(max_workers=num_workers)

        app_instance['process_pool'] = pool

        yield

        logger.debug("Shutting down process pool")

        pool.shutdown()

    return process_pool
