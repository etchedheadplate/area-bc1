import os
import logging


main_logger = logging.getLogger(__name__)
main_logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('area-bc1.log')
file_handler.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

main_logger.addHandler(file_handler)
main_logger.addHandler(console_handler)
