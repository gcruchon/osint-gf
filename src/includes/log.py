import logging

logging.basicConfig(
    filename="logs/osint-gf.log",
    encoding="utf-8",
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

def info(msg):
    logging.info(msg)

def debug(msg):
    logging.debug(msg)

def error(msg):
    logging.error(msg)