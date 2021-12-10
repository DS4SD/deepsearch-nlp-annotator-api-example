import logging
_log = logging.getLogger(__name__)


def health():
    return {"status": "OK"}
