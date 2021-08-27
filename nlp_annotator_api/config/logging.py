import logging.config

DEFAULT_LOGGING_CONFIG = {
    'version': 1,
    'loggers': {
        # '': {
        #     'level': 'INFO',
        #     'handlers': ['console']
        # },
        'connexion': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'nlp_annotator_api': {
            'level': 'DEBUG',
            'handlers': ['console']
        },
        'aiohttp': {
            'level': 'DEBUG',
            'handlers': ['console']
        }
    },
    'formatters': {
        'default': {
            'format': '[%(asctime)s - %(name)s] - %(levelname)s - %(message)s',
        }
    },
    # 'filters': {
    #
    # },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
        }
    }
}


def setup_logging():
    logging.config.dictConfig(DEFAULT_LOGGING_CONFIG)
