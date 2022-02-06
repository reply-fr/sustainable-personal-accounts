
# credit:
# - https://towardsdatascience.com/the-reusable-python-logging-template-for-all-your-data-science-apps-551697c8540

import logging
import os
import sys


def setup_logging(environ=None,
                  format="%(asctime)s - %(message)s",
                  name=None,
                  stream=sys.stdout):
    logger = logging.getLogger(name)
    environ = environ if environ else os.environ
    verbosity = environ.get('VERBOSITY', 'DEBUG')
    logger.setLevel(logging.__dict__[verbosity])
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(format))
    logger.handlers.clear()
    logger.addHandler(handler)
    return logger
