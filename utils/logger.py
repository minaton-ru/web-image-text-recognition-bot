import logging
from logging.handlers import RotatingFileHandler

from config import LOG_LEVEL


file_handler = RotatingFileHandler("bot.log",
                                   maxBytes=3*1024*1024,  # 3 Mb
                                   backupCount=3,
                                   encoding="utf-8")

logging.basicConfig(level=LOG_LEVEL,
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
                    handlers=[file_handler, logging.StreamHandler()])
