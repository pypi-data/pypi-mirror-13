import logging

from sen.constants import FALLBACK_LOG_PATH

__version__ = "0.1"


def set_logging(name="sen", level=logging.DEBUG, path=FALLBACK_LOG_PATH):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    handler = logging.FileHandler(path)
    handler.setLevel(logging.DEBUG)
    # handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter('%(asctime)s %(name)-18s %(levelname)-6s %(message)s',
                                  '%H:%M:%S')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
