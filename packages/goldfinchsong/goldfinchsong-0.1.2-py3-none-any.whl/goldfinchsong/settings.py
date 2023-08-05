"""Settings module.

Attributes:
    LOGGER_CONFIG (dict): Logging configuration settings. Includes formatters, handlers, loggers
"""

LOGGER_CONFIG = {
    'version': 1,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        'simple': {
            'format': '%(levelname)s %(asctime)s %(module)s %(message)s'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        }
    },
    'loggers': {
        'goldfinchsong': {
            'handlers': ['console'],
            'propagate': True,
            'level': 'INFO',
        },
    }
}