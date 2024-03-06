import logging
from logging.handlers import TimedRotatingFileHandler
import config


main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.DEBUG)

file_handler = TimedRotatingFileHandler(config.bot_log_file, when='D', interval=1, backupCount=config.bot_log_age)
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s')

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

main_logger.addHandler(file_handler)
main_logger.addHandler(console_handler)