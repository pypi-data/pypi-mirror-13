from django.conf import settings


PDFKIT_OPTIONS = {
    'page-size': 'Letter',
    'margin-top': '1.2in',
    'margin-right': '0.75in',
    'margin-bottom': '1.2in',
    'margin-left': '0.75in',
    'encoding': "UTF-8",
    'no-outline': None,
    'quiet': '',
}

DEFAULT_LOGGING_FORMATTER = {
    'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
}

DEFAULT_LOGGING_HANDLER = {
    'level': 'INFO',
    'class': 'logging.StreamHandler',
    'formatter': 'lightpdf'
}

DEFAULT_LOGGER = {
    'handlers': ['lightpdf'],
    'level': 'INFO',
}


LOGGING_VERSION = settings.LOGGING.get('version', 1)
LOGGING_FORMATTER = settings.LOGGING.get('formatters', {}).get('lightpdf', DEFAULT_LOGGING_FORMATTER)
LOGGING_HANDLER = settings.LOGGING.get('handlers', {}).get('lightpdf', DEFAULT_LOGGING_HANDLER)
LOGGING_LOGGER = settings.LOGGING.get('logger', {}).get('lightpdf', DEFAULT_LOGGER)

LOGGING_CONFIG = {
    'version': LOGGING_VERSION,
    'disable_existing_loggers': False,
    'formatters': {
        'lightpdf': LOGGING_FORMATTER,
    },
    'handlers': {
        'lightpdf': LOGGING_HANDLER,
    },
    'loggers': {
        'lightpdf': LOGGING_LOGGER,
    }
}


LIGHTPDF_PDFKIT_OPTIONS = getattr(settings, 'LIGHTPDF_PDFKIT_OPTIONS', PDFKIT_OPTIONS)
LIGHTPDF_LOGGING_CONFIG = getattr(settings, 'LIGHTPDF_LOGGING_CONFIG', LOGGING_CONFIG)
