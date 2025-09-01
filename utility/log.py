import logging

LEVEL = logging.DEBUG
FORMAT = '%(asctime)s.%(msecs)03d [%(levelname)-7s] [%(name)-10s] : %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def setup_logging():
    logging.basicConfig(format=FORMAT, level=LEVEL, datefmt=DATE_FORMAT)
